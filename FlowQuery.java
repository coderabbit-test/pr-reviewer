package com.flecso.employer.graphql.query;

import com.coxautodev.graphql.tools.GraphQLQueryResolver;
import com.flecso.employer.central.entity.GoalTemplate;
import com.flecso.employer.dto.*;
import com.flecso.employer.dto.analytics.*;
import com.flecso.employer.dto.charts.Chart;
import com.flecso.employer.dto.charts.ChartDataState;
import com.flecso.employer.dto.charts.ChartError;
import com.flecso.employer.dto.charts.ChartMetadata;
import com.flecso.employer.dto.filters.IssueFilterConditions;
import com.flecso.employer.dto.rechart.ChartKey;
import com.flecso.employer.entity.IntegrationType;
import com.flecso.employer.entity.IssueUnits;
import com.flecso.employer.central.entity.MetricConfig;
import com.flecso.employer.entity.SDLCStageConfig;
import com.flecso.employer.exception.ConfigurationException;
import com.flecso.employer.exception.GlobalExceptionHandler;
import com.flecso.employer.exception.NoIntegrationException;
import com.flecso.employer.repository.IssueUnitCustomRepoImpl;
import com.flecso.employer.repository.IssueUnitsRepo;
import com.flecso.employer.repository.SDLCStageConfigRepo;
import com.flecso.employer.service.DateUtil;
import com.flecso.employer.service.TeamService;
import com.flecso.employer.service.goal.ThresholdService;
import com.flecso.employer.service.integration.IntegrationService;
import com.flecso.employer.util.ChartUtilService;
import com.flecso.employer.util.ColorUtil;
import com.flecso.employer.util.Constants;
import com.flecso.employer.util.CoreUtil;
import com.github.sisyphsu.dateparser.DateParserUtils;
import com.google.common.collect.Sets;
import com.google.gson.Gson;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.commons.lang3.tuple.Triple;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

import static com.flecso.employer.dto.analytics.Metric.*;

@Component
public class FlowQuery extends BaseQuery implements GraphQLQueryResolver {

    @Autowired
    IntegrationService integrationService;
    @Autowired
    private IssueUnitsRepo issueUnitsRepo;
    @Autowired
    private TeamService teamService;
    @Autowired
    private ChartUtilService chartUtilService;
    @Autowired
    private IssueUnitCustomRepoImpl issueUnitCustomRepo;
    @Autowired
    private ThresholdService thresholdService;

    @Autowired
    private GlobalExceptionHandler globalExceptionHandler;
    @Autowired
    private TeamQuery teamQuery;
    @Autowired
    private SDLCStageConfigRepo sdlcStageConfigRepo;

    ExecutorService executorService = Executors.newFixedThreadPool(8);

    Gson gson = new Gson();

    Logger logger = LoggerFactory.getLogger(FlowQuery.class);

    public Chart getThroughputValueStreamByType(String metricStr, String granularityStr, String breakdown, Filter filter) throws Exception {
        Granularity granularity = StringUtils.isBlank(granularityStr) ? Granularity.WEEK : Granularity.valueOf(granularityStr);
        setDateRangeFromSprintId(filter);
        List<Map<String, Object>> dataList = new ArrayList<>();
        List<Map<String, Object>> prevPeriodDataList = new ArrayList<>();
        Pair<PreviousPeriodStat, Double> prevPeriodStatAndTotalPair = Pair.of(PreviousPeriodStat.builder().build(), 0.0);
        Threshold threshold = null;
        Metric metric = Metric.valueOf(metricStr);
        MetricConfig metricConfig = getMetricConfig(metric.name());
        ChartMetadata chartMetadata = getChartMetaData(metricConfig);
        Chart chart = Chart.builder().chartMetadata(chartMetadata).build();
        try {
            isIntegrationActive(filter, metricConfig.getSource());
            dataList = getValueStreamData(filter, metricConfig, granularity);
            double cumulativeOutflow = 0;
            double cumulativeInflow = 0;
            if (dataList.size() - 1 > 0) {
                cumulativeOutflow = (int) dataList.get(dataList.size() - 1).get("cumulativeOutflow");
                cumulativeInflow = (int) dataList.get(dataList.size() - 1).get("cumulativeInflow");
            }
            double throughput = 0.0;
            if (cumulativeInflow != 0) {
                throughput = (cumulativeOutflow*100) / cumulativeInflow;
            }
            if (CollectionUtils.isNotEmpty(dataList)) {
                switch (metric) {
                    case ISSUE_THROUGHPUT:
                        threshold = thresholdService.getThreshold(filter.getOrgId(), filter.getTeamId(), metricConfig, throughput, granularity);
                        break;
                    case BUG_THROUGHPUT:
                        dataList = convertIssueThroughputData(dataList);
                        prevPeriodDataList = convertIssueThroughputData(getValueStreamData(filter.lastPeriodFilterInstance(), metricConfig, granularity));
                        throughput = Math.round(throughput * 100.0) / 100.0;
                        if (CollectionUtils.isNotEmpty(prevPeriodDataList) && CollectionUtils.isNotEmpty(dataList)) {
                            prevPeriodStatAndTotalPair = Pair.of(teamQuery.getPreviousPeriodStat((int) (double) dataList.get(dataList.size() - 1).get("y"), (int) (double) prevPeriodDataList.get(prevPeriodDataList.size() - 1).get("y"), metricConfig), throughput);
                        } else {
                            prevPeriodStatAndTotalPair = Pair.of(PreviousPeriodStat.builder().build(), throughput);
                        }
                        break;
                }
            }
        } catch (NoIntegrationException noIntegrationException) {
            chart.setChartDataState(ChartDataState.NO_INTEGRATION.name());
            chart.setChartError(ChartError.builder().message(noIntegrationException.getMessage()).link(noIntegrationException.getLink()).build());
            return chart;
        } catch (ConfigurationException configurationException) {
            chart.setChartDataState(ChartDataState.NOT_CONFIGURED.name());
            chart.setChartError(ChartError.builder().message(configurationException.getMessage()).link(configurationException.getLink()).build());
            return chart;
        } catch (Exception ex) {
            globalExceptionHandler.handleGeneralException(ex);
        }

        return metric.equals(ISSUE_THROUGHPUT) ? chartUtilService.getChartForValueStreamFromProjectData(metricConfig, dataList, threshold, chartMetadata) : chartUtilService.getChartFromProjectData(null, dataList, prevPeriodStatAndTotalPair, chartMetadata, granularity);
    }
}
