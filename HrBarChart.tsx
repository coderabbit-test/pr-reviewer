import { Box, Flex, Text } from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '@chakra-ui/react';

interface HrBarChartProps {
  data: any;
  keys: any;
  chartMetadata: any;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <Box bg="white" p={2} boxShadow="md" borderRadius="md" border="none">
        <Flex gap={0.5} flexDirection={'column'} fontSize={'sm'}>
          <Text fontWeight={'bold'}>{label}</Text>
          <Text color="text.secondary2">
            Acceptance rate:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.value}%
            </Text>
          </Text>
          <Text color="text.secondary2">
            Acceptance Count:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.acceptanceCount}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Avg Active Users:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.avgActiveUsers}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Line Accepted:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.lineAccepted}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Line Suggested:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.lineSuggested}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Max Active Users:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.maxActiveUsers}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Suggestion Count:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.suggestionCount}
            </Text>
          </Text>
        </Flex>
      </Box>
    );
  }
  return null;
};

export const HrBarChart = ({ data, chartMetadata }: HrBarChartProps) => {
  const { colors } = useTheme();
  const transformedData = Object.entries(data?.data)?.map(
    ([language, stats]: [string, any]) => ({
      language: language.charAt(0).toUpperCase() + language.slice(1),
      acceptanceRate: parseFloat(stats.acceptanceRate),
      acceptanceCount: parseInt(stats.acceptanceCount),
      avgActiveUsers: parseFloat(stats.avgActiveUsers).toFixed(2),
      lineAccepted: parseInt(stats.lineAccepted),
      lineSuggested: parseInt(stats.lineSuggested),
      maxActiveUsers: parseInt(stats.maxActiveUsers),
      suggestionCount: parseInt(stats.suggestionCount),
    })
  );
  transformedData?.sort((a, b) => b.acceptanceRate - a.acceptanceRate);

  const CustomBarLabel = (props: any) => {
    const { x, y, width, value } = props;
    return (
      <text
        x={x + width + 10}
        y={y + 10}
        fill="#667085"
        fontSize={11}
        fontWeight={500}
        textAnchor="start"
      >
        {`${value}%`}
      </text>
    );
  };

  return (
    <Box height="100%" width="100%">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={transformedData}
          margin={{ top: 10, right: 10, left: 60, bottom: 10 }}
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            axisLine={{ stroke: '#E2E8F0', strokeWidth: 1 }}
            tickLine={false}
            style={{ fontSize: 11, fontWeight: 400, fill: colors.text.primary }}
            label={{
              value: chartMetadata?.xlabel,
              position: 'bottom',
              offset: 0,
              style: {
                textAnchor: 'middle',
                fontSize: 11,
              },
            }}
          />
          <YAxis
            type="category"
            dataKey="language"
            axisLine={{ stroke: '#E2E8F0', strokeWidth: 1 }}
            tickLine={false}
            interval={0}
            style={{ fontSize: 13, fontWeight: 400, fill: colors.text.primary }}
            label={{
              value: chartMetadata?.ylabel,
              angle: -90,
              position: 'outsideLeft',
              fontSize: 11,
              fontWeight: 400,
              dy: 40,
              dx: -60,
              zIndex: 1000,
            }}
          />
          <Tooltip
            cursor={false}
            content={<CustomTooltip />}
            wrapperStyle={{ outline: 'none' }}
          />
          <Bar
            dataKey="acceptanceRate"
            fill={colors.primary}
            radius={[0, 4, 4, 0]}
            barSize={20}
            label={<CustomBarLabel />}
            animationDuration={1000}
            animationBegin={0}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};import { Box, Flex, Text } from '@chakra-ui/react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '@chakra-ui/react';

interface HrBarChartProps {
  data: any;
  keys: any;
  chartMetadata: any;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <Box bg="white" p={2} boxShadow="md" borderRadius="md" border="none">
        <Flex gap={0.5} flexDirection={'column'} fontSize={'sm'}>
          <Text fontWeight={'bold'}>{label}</Text>
          <Text color="text.secondary2">
            Acceptance rate:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.value &&
              !isNaN(payload[0]?.value) &&
              payload[0]?.value > 0
                ? `${payload[0]?.value}%`
                : '0'}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Acceptance Count:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.acceptanceCount}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Avg Active Users:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.avgActiveUsers}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Line Accepted:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.lineAccepted}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Line Suggested:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.lineSuggested}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Max Active Users:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.maxActiveUsers}
            </Text>
          </Text>
          <Text color="text.secondary2">
            Suggestion Count:{' '}
            <Text as="span" color="text.primary">
              {payload[0]?.payload.suggestionCount}
            </Text>
          </Text>
        </Flex>
      </Box>
    );
  }
  return null;
};

export const HrBarChart = ({ data, chartMetadata }: HrBarChartProps) => {
  const { colors } = useTheme();
  const transformedData = Object.entries(data?.data)?.map(
    ([language, stats]: [string, any]) => ({
      language: language.charAt(0).toUpperCase() + language.slice(1),
      acceptanceRate: parseFloat(stats.acceptanceRate),
      acceptanceCount: parseInt(stats.acceptanceCount),
      avgActiveUsers: parseFloat(stats.avgActiveUsers).toFixed(2),
      lineAccepted: parseInt(stats.lineAccepted),
      lineSuggested: parseInt(stats.lineSuggested),
      maxActiveUsers: parseInt(stats.maxActiveUsers),
      suggestionCount: parseInt(stats.suggestionCount),
    })
  );
  transformedData?.sort((a, b) => b.acceptanceRate - a.acceptanceRate);

  const CustomBarLabel = (props: any) => {
    const { x, y, width, value } = props;
    if (isNaN(value) || value == null || value <= 0) {
      return null;
    }
    return (
      <text
        x={x + width + 10}
        y={y + 10}
        fill="#667085"
        fontSize={11}
        fontWeight={500}
        textAnchor="start"
      >
        {`${value}%`}
      </text>
    );
  };

  return (
    <Box height="100%" width="100%">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={transformedData}
          margin={{ top: 10, right: 10, left: 60, bottom: 10 }}
        >
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            axisLine={{ stroke: '#E2E8F0', strokeWidth: 1 }}
            tickLine={false}
            style={{ fontSize: 11, fontWeight: 400, fill: colors.text.primary }}
            label={{
              value: chartMetadata?.xlabel,
              position: 'bottom',
              offset: 0,
              style: {
                textAnchor: 'middle',
                fontSize: 11,
              },
            }}
          />
          <YAxis
            type="category"
            dataKey="language"
            axisLine={{ stroke: '#E2E8F0', strokeWidth: 1 }}
            tickLine={false}
            interval={0}
            style={{ fontSize: 13, fontWeight: 400, fill: colors.text.primary }}
            label={{
              value: chartMetadata?.ylabel,
              angle: -90,
              position: 'outsideLeft',
              fontSize: 11,
              fontWeight: 400,
              dy: 40,
              dx: -60,
              zIndex: 1000,
            }}
          />
          <Tooltip
            cursor={false}
            content={<CustomTooltip />}
            wrapperStyle={{ outline: 'none' }}
          />
          <Bar
            dataKey="acceptanceRate"
            fill={colors.primary}
            radius={[0, 4, 4, 0]}
            barSize={20}
            label={<CustomBarLabel />}
            animationDuration={1000}
            animationBegin={0}
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};
