package com.flecso.employer.graphql.query;

import com.coxautodev.graphql.tools.GraphQLQueryResolver;
import com.flecso.employer.central.entity.AccountStateType;
import com.flecso.employer.dto.DependencyVulDetails;
import com.flecso.employer.dto.InProgressWorkItems;
import com.flecso.employer.dto.analytics.*;
import com.flecso.employer.dto.analytics.build.BuildDetails;
import com.flecso.employer.dto.analytics.build.BuildStageDetails;
import com.flecso.employer.dto.analytics.prmetricdetail.PRMetricDetails;
import com.flecso.employer.dto.filters.IssueFilterConditions;
import com.flecso.employer.entity.*;
import com.flecso.employer.central.entity.MetricConfig;
import com.flecso.employer.exception.ConfigurationException;
import com.flecso.employer.exception.ErrorCode;
import com.flecso.employer.exception.GlobalExceptionHandler;
import com.flecso.employer.repository.*;
import com.flecso.employer.service.ContributorService;
import com.flecso.employer.service.CustomMetricService;
import com.flecso.employer.service.DateUtil;
import com.flecso.employer.service.MetricsMetadataService;
import com.flecso.employer.service.TeamService;
import com.flecso.employer.service.deliverable.DeliverableService;
import com.flecso.employer.strategy.GitMetricCalculationStrategy;
import com.flecso.employer.util.Constants;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.ObjectUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Component
public class DataDetailsQuery extends BaseQuery implements GraphQLQueryResolver {

    @Autowired
    IssueUnitCustomRepoImpl issueUnitCustomRepo;
    @Autowired
    BuildDeploymentUnitCustomRepo buildDeploymentUnitCustomRepo;

    @Autowired
    GitUnitPrCustomRepoImpl gitUnitPrCustomRepo;

    @Autowired
    VulnerabilityUnitsCustomRepo vulnerabilityUnitsCustomRepo;

    @Autowired
    EventLogGitCustomRepoImpl eventLogGitCustomRepo;

    @Autowired
    ContributorService contributorService;

    @Autowired
    Games24X7CustomRepoImpl games24X7CustomRepo;

    @Autowired
    TeamService teamService;
    @Autowired
    private CustomMetricService customMetricService;
    @Autowired
    private GlobalExceptionHandler globalExceptionHandler;

    @Autowired
    private WorkBreakdownCustomRepo workBreakdownCustomRepo;
    @Autowired
    private MetricsMetadataService metricsMetadataService;
    @Autowired
    private RecruitCRMCustomQueryRepoImpl recruitCRMCustomQueryRepo;
    @Autowired
    private DeliverableService deliverableService;
    @Autowired
    private GitMetricCalculationStrategy gitMetricCalculationStrategy;
    @Autowired
    private SprintCustomRepoImpl sprintCustomRepo;

    public CommitMetricDetails getCommitReportDetail(String metric, String granularity, Filter filter, Integer pageNumber, Integer pageSize) throws Exception {
        setDateRangeFromSprintId(filter);
        MetricConfig metricConfig = getMetricConfig(metric);
        Metric metricType = Metric.valueOf(metric);
        Pair<List<String>, List<String>> assigneeAndProjectList = getAssigneeAndProjectList(filter, metricConfig);
        List<String> repoList = assigneeAndProjectList.getRight();
        List<String> assignees = assigneeAndProjectList.getLeft();
        List<String> prIds = filter.getPrViewFilters() != null && CollectionUtils.isNotEmpty(filter.getPrViewFilters().getPrIds()) ? filter.getPrViewFilters().getPrIds() : new ArrayList<>();

        CommitMetricDetails commitMetricDetails = gitUnitPrCustomRepo.getCommitReportDetailList(filter.getOrgId(), metricType, filter.getLocalStartDateFromEndDate(), filter.getEndDate(),assignees, repoList, prIds, filter.getTimeZone(), pageNumber, pageSize);
        return commitMetricDetails;
    }
}
