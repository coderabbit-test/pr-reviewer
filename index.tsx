import { Box, Flex, Text, Tooltip } from '@chakra-ui/react';
import { useEffect, useState } from 'react';

export default function CustomLegend({
  barProps,
  setBarProps,
  keys,
  w,
  ...props
}: any) {
  const showReset = !keys.every((item: any) => barProps[item.key]);
  const [hasShownTooltip, setHasShownTooltip] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const resetSelected = () => {
    setBarProps(
      keys?.reduce(
        (a: any, { key }: any) => {
          a[key] = true;
          return a;
        },
        {
          hover: null,
        }
      )
    );
  };

  return (
    <Box flexDirection={'column'} padding={'0 20px'} w={w ? w : 220}>
      <Tooltip
        label={'Double-click on legend to isolate a single metric.'}
        isOpen={showTooltip}
        placement="top"
        w={170}
        fontSize={'xs'}
      >
        <Text
          fontWeight={600}
          fontSize={'xs'}
          textDecor={'underline'}
          w={'fit-content'}
          mb={1}
          onClick={() => {
            if (!showReset) {
              return;
            }
            resetSelected();
          }}
          visibility={showReset ? 'visible' : 'hidden'}
          cursor={'pointer'}
        >
          Reset
        </Text>
      </Tooltip>
      {keys?.map((entry: any) => {
        const isLine = ['line_chart', 'dashed_line_chart'].includes(
          entry?.chartType
        );
        return (
          <Flex
            key={entry?.key}
            align={'center'}
            w={'fit-content'}
            cursor={'pointer'}
            onDoubleClick={() => {
              setBarProps(
                keys?.reduce(
                  (a: any, { key }: any) => {
                    a[key] = entry?.key === key ? true : false;
                    return a;
                  },
                  {
                    hover: null,
                  }
                )
              );
            }}
            onClick={() => {
              if (!hasShownTooltip) {
                setHasShownTooltip(true);
                setShowTooltip(true);
                setTimeout(() => {
                  setShowTooltip(false);
                }, 1500);
              }

              setBarProps((barProps: any) => {
                return {
                  ...barProps,
                  [entry?.key]: !barProps[entry?.key],
                  hover: null,
                };
              });
            }}
            onMouseEnter={() => {
              if (!barProps[entry?.key]) {
                return;
              }
              setBarProps((barProps: any) => {
                return { ...barProps, hover: entry.key };
              });
            }}
            onMouseLeave={() => {
              setBarProps((barProps: any) => {
                return { ...barProps, hover: null };
              });
            }}
          >
            {isLine ? (
              <svg width="20" height="3" style={{ marginRight: '5px' }}>
                <line
                  x1="0"
                  y1="1.5"
                  x2="20"
                  y2="1.5"
                  stroke={barProps[entry?.key] ? entry?.color : 'grey'}
                  strokeWidth="3"
                  strokeDasharray={
                    entry?.chartType === 'dashed_line_chart' ? '2 2' : 'none'
                  }
                />
              </svg>
            ) : (
              <svg width="20" height="20" style={{ marginRight: '5px' }}>
                <circle
                  cx="10"
                  cy="10"
                  r="5"
                  fill={barProps[entry?.key] ? entry?.color : 'grey'}
                  fillOpacity={
                    entry?.chartType === 'dashed_bar_chart' ? 0.2 : 1
                  }
                  stroke={
                    entry?.chartType === 'dashed_bar_chart'
                      ? entry?.color
                      : 'none'
                  }
                  strokeDasharray={
                    entry?.chartType === 'dashed_bar_chart' ? '2 2' : 'none'
                  }
                />
              </svg>
            )}
            <Text
              _hover={
                barProps[entry?.key]
                  ? { color: entry?.color, fontWeight: 600 }
                  : { color: 'grey' }
              }
              color={barProps[entry?.key] ? entry?.color : 'grey'}
              decoration={barProps[entry?.key] ? 'auto' : 'line-through'}
            >
              {entry?.name}
            </Text>
          </Flex>
        );
      })}
    </Box>
  );
}
