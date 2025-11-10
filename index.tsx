import { Box, Button } from '@chakra-ui/react';
import { useCallback, useEffect, useState } from 'react';
import BottomSection from './BottomSection';
import TopSection from './TopSection';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { useDetailChartsGql } from '../graphql/index';
import { ISelect } from '../../formComponents/customSelect';
import { durationData, splitTime } from '../../shared/utils';
import Breadcrumbs from '../../appBreadcrumb';
import useQueryState from '../../hooks/useQueryState';
import { removeEmptyQueryParams } from '../../hooks/queryString';
import { useDashboardStore } from '../../hooks/useDashboardStore';
import { SlideInfoDrawer } from '../../infoSlidebar/SlideInfoDrawer';
import {
  controlChartKeys,
  getViewForFilter,
} from '../helpers/metricCard.utils';

interface metricDetailProps {
  initialTeam?: string;
}

export const MetricDetails = ({ initialTeam }: metricDetailProps) => {
  const [searchParams] = useSearchParams();
  const metricType = searchParams.get('type');
  const project = searchParams.get('project');
  const location = useLocation();
  const navigate = useNavigate();

  const [startDate, setStartDate] = useQueryState('start');
  const [endDate, setEndDate] = useQueryState('end');
  const [duration, setDuration] = useQueryState('duration');
  const [sprintId, setSprintId] = useQueryState('sprintId');
  const [sprintName, setSprintName] = useQueryState('sprint');
  const [team, setTeam] = useQueryState('team');
  const [view, setView] = useQueryState('view');
  const [breakdownBy, setBreakdownBy] = useQueryState('breakdown');
  const [showControlChart, setShowControlChart] =
    useQueryState('showControlChart');
  const { selectedTeam, selected, setSelectedTeam, setSelected } =
    useDashboardStore();

  const [openDrawer, setOpenDrawer] = useState(false);

  const handleDrawerClose = useCallback(
    () => setOpenDrawer(false),
    [openDrawer]
  );

  const [breakdown, setBreakdown] = useState<ISelect>({
    value: '',
    label: '-',
  });

  const [periodOptions, setPeriodOptions] = useState<any>(durationData);

  const [viewToggle, setViewToggle] = useState<string>('Week');
  const [repos, setRepos] = useState<string[]>([]);
  const [filterBy, setFilterBy] = useState<{
    value: string;
    label: string;
  }>({ value: 'team', label: 'Team' });
  const [controlChart, setControlChart] = useState(false);

  const { data, isLoading, isFetching, refetch } = useDetailChartsGql(
    selected.startDate,
    selected.endDate,
    metricType as string,
    breakdown.value,
    filterBy.value === 'repo' ? '' : selectedTeam.value,
    selected?.sprintId,
    project || '',
    filterBy.value === 'team' ? [] : repos.map((el: any) => el.value),
    viewToggle.toUpperCase(),
    getViewForFilter(metricType, ''),
    undefined,
    showControlChart
  );

  const handelReloadClick = async () => {
    await refetch();
  };

  useEffect(() => {
    if (selected.duration === 'Sprint') {
      setViewToggle('Day');
    } else {
      setViewToggle('Week');
    }
  }, [selected.duration]);

  const modifiedData = [
    'MEAN_TIME_TO_RECOVERY',
    'LEAD_TIME_FOR_CHANGE',
    'PR_CYCLE_TIME',
    'CODING_CYCLE_TIME',
    'PICKUP_CYCLE_TIME',
    'MERGE_CYCLE_TIME',
    'TASK_LEAD_TIME',
    'BUG_LEAD_TIME',
    'ISSUE_CYCLE_TIME',
    'MEETING_TIME',
    'DEPLOY_CYCLE_TIME',
    'DELIVERY_LEAD_TIME',
    'BACKLOG_CYCLE_TIME',
    'TEST_RUN_TIME',
    'CUSTOM',
  ].includes(data?.chartMetadata?.chartKey)
    ? {
        ...data,
        average:
          data?.average && data?.chartMetadata?.dataType == 'INTEGER'
            ? data?.average
            : data?.average && data?.chartMetadata?.dataType == 'TIME'
            ? splitTime(parseInt(data?.average) / 60)
            : data?.average && data?.chartMetadata?.dataType == 'PERCENTAGE'
            ? data?.average
            : data?.average && splitTime(parseInt(data?.average) / 60),
        chartMetadata: {
          ...data.chartMetadata,
          ylabel:
            data?.chartMetadata?.chartKey === 'CUSTOM'
              ? data?.chartMetadata.ylabel
              : 'Hour',
        },
       data: data?.data?.map((item: any) => ({
          ...item,
          y:
            data?.chartMetadata?.chartKey === 'CUSTOM'
              ? Number(item.y)
              : Number(item.y) / 60,
          clusterP90ToP95: Number(item.clusterP90ToP95) / 60 || 0,
          clusterP95ToP100: Number(item.clusterP95ToP100) / 60 || 0,
          clusterP0ToP5: Number(item.clusterP0ToP5) / 60 || 0,
          clusterP5ToP10: Number(item.clusterP5ToP10) / 60 || 0,
        })),

          return convertedItem;
        }),
        keys: data?.keys?.map((key: any) =>
          key.name === 'Minutes' ? { ...key, name: 'Hours' } : key
        ),
        refLines: data?.refLines,
      }
    : data;

  useEffect(() => {
    if (typeof selected !== 'undefined') {
      selected.startDate && setStartDate(selected.startDate);
      selected.endDate && setEndDate(selected.endDate);
      selected.duration && setDuration(selected.duration);
      selected?.sprintId === ''
        ? removeEmptyQueryParams({ sprintId: '' })
        : setSprintId(selected?.sprintId);
      selected?.sprintName === ''
        ? removeEmptyQueryParams({ sprint: '' })
        : setSprintName(selected?.sprintName);
    }

    if (typeof selectedTeam !== 'undefined') {
      selectedTeam.value === ''
        ? removeEmptyQueryParams({ team: '' })
        : setTeam(selectedTeam.value);
    }

    if (typeof viewToggle !== 'undefined') {
      viewToggle && setView(viewToggle);
    }

    if (typeof breakdown.value !== 'undefined') {
      breakdown.value === ''
        ? removeEmptyQueryParams({ breakdown: '' })
        : setBreakdownBy(breakdown.value);
    }
  }, [selected, selectedTeam.value, viewToggle, breakdown.value]);

  useEffect(() => {
    team &&
      setSelectedTeam({
        value: team === 'Organisation' ? '' : team,
        label: team,
      });

    duration || selected.duration
      ? setSelected(
          periodOptions
            .filter(
              (item: any) =>
                item.duration === duration ||
                item.duration === selected.duration
            )
            .map((el: any) =>
              el.duration === 'Custom' ||
              el.duration === 'Today' ||
              el.duration === 'Month' ||
              el.duration === 'Quarter'
                ? {
                    ...el,
                    startDate: startDate || selected.startDate,
                    endDate: endDate || selected.endDate,
                  }
                : el.duration === 'Sprint'
                ? {
                    ...el,
                    startDate: startDate || selected.startDate,
                    endDate: endDate || selected.endDate,
                    sprintId: sprintId || selected.sprintId,
                    sprintName: sprintName || selected.sprintName,
                  }
                : el
            )[0]
        )
      : setSelected(periodOptions[3]);

    breakdownBy && setBreakdown({ value: breakdownBy, label: breakdownBy });

    view && setViewToggle(view);

    showControlChart && setControlChart(showControlChart);
  }, []);

  useEffect(() => {
    if (controlChartKeys.includes(metricType as string)) {
      setShowControlChart(controlChart);
    }
  }, [controlChart]);

  return (
    <Box
      display={'flex'}
      flexDirection={'column'}
      width={'100%'}
      minHeight={'100%'}
    >
      {location?.pathname !== '/custom-dashboard' ? (
        <Breadcrumbs />
      ) : (
        <Button
          onClick={() => navigate(-1)}
          size="sm"
          variant="link"
          w={'fit-content'}
        >
          Back
        </Button>
      )}
      <Box mt={1}>
        <TopSection
          data={modifiedData}
          isLoading={isLoading}
          setOpenDrawer={setOpenDrawer}
          openDrawer={openDrawer}
        />
        <BottomSection
          breakdown={breakdown}
          setBreakdown={setBreakdown}
          selected={selected}
          setSelected={setSelected}
          selectedTeam={selectedTeam}
          setSelectedTeam={setSelectedTeam}
          isLoading={isLoading}
          isFetching={isFetching}
          data={modifiedData}
          viewToggle={viewToggle}
          setViewToggle={setViewToggle}
          repos={repos}
          setRepos={setRepos}
          filterBy={filterBy}
          setFilterBy={setFilterBy}
          handelReloadClick={handelReloadClick}
          controlChart={controlChart}
          setControlChart={setControlChart}
        />
      </Box>
      {openDrawer && (
        <SlideInfoDrawer
          handelDrawerClose={handleDrawerClose}
          openDrawer={openDrawer}
          title={data?.chartMetadata?.chartTitle}
          chartKey={data?.chartMetadata?.chartKey}
          item={data}
        />
      )}
    </Box>
  );
};
