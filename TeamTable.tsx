import {
  Box,
  Button,
  Flex,
  IconButton,
  ListIcon,
  ListItem,
  Text,
  Tooltip,
  UnorderedList,
  useTheme,
  useToast,
  Image,
} from '@chakra-ui/react';
import React, { useEffect, useMemo } from 'react';
import Present from '../assets/Present.svg';
import NotPresent from '../assets/notPresent.svg';

import {
  ConfirmButton,
  DataGrid,
  Loader,
  useToastHook,
} from '@devd-client/devd/components';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@devd-client/api';
import { createColumnHelper } from '@tanstack/react-table';
import { QUERY_KEYS, useFetchTeams } from '../apis';
import { AiOutlineMinusSquare, AiOutlinePlusSquare } from 'react-icons/ai';
import { useQueryClient } from '@tanstack/react-query';
import { MdOutlineEdit, MdPersonAddAlt } from 'react-icons/md';
import { TEAM_DETAILS_QUERY_KEYS } from '@devd-client/devd/team-details';

interface TeamViewProps {
  team: string;
  setTeamLength: any;
  appState?: any;
  teamLength?: number;
  plan?: string;
}

const TeamView: React.FC<TeamViewProps> = ({
  team,
  setTeamLength,
  appState,
  teamLength,
  plan,
}) => {
  const queryClient = useQueryClient();
  const { colors } = useTheme();
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);
  const [newToast] = useToastHook();

  const { data: teamsData, isFetching: teamsDataLoading } = useFetchTeams(team);

  const rows: any[] = useMemo(() => teamsData?.dto || [], [teamsData?.dto]);

  useEffect(() => {
    setTeamLength(rows.length);
  }, [rows, setTeamLength]);

  const columnHelper = createColumnHelper<any>();

  const columns = useMemo(
    () => [
      columnHelper.accessor('name', {
        cell: (info) => {
          return (
            <Box pl={`${info.row.depth * 3}rem`}>
              {info.row.getCanExpand() ? (
                <>
                  <Button
                    variant={'unstyled'}
                    minWidth={0}
                    onClick={info.row.getToggleExpandedHandler()}
                  >
                    {info.row.getIsExpanded() ? (
                      <AiOutlineMinusSquare
                        size={18}
                        color={colors.text.primary}
                      />
                    ) : (
                      <AiOutlinePlusSquare
                        size={18}
                        color={colors.text.primary}
                      />
                    )}
                  </Button>
                </>
              ) : (
                ''
              )}{' '}
              {info.getValue()}
            </Box>
          );
        },
        header: 'Team Name',
      }),

      columnHelper.accessor('description', {
        cell: (info) => {
          if (!info.getValue()) {
            return <Box color="orange.600">No Description Added</Box>;
          } else {
            return info.getValue();
          }
        },
        header: 'Description',
        size: 360,
      }),

      columnHelper.accessor('managers', {
        cell: (info) => {
          let count = 0;
          info.row.original.subTeams.forEach((item: any) => {
            count += item.managers.length;
          });
          return (
            <Flex flexWrap="wrap">
              {info?.getValue()?.length > 0 ? (
                <Box>
                  {info?.getValue()?.map((item: string, idx: number) => (
                    <Text mr={2} key={`manager-${idx}`}>
                      {item}
                      {info.getValue().length - 1 !== idx && ','}
                    </Text>
                  ))}
                  {info.row.original.subTeams.length > 0 ? (
                    <Text>+{count} in subteams</Text>
                  ) : (
                    ''
                  )}
                </Box>
              ) : (
                <Box>
                  <Text color={'gray.400'} fontFamily={'heading'}>
                    No Manager Assigned
                  </Text>
                  {info.row.original.subTeams.length > 0 ? (
                    <Text>+{count} in subteams</Text>
                  ) : (
                    ''
                  )}
                </Box>
              )}
            </Flex>
          );
        },
        header: 'Managers',
      }),
      columnHelper.accessor('memberCount', {
        cell: (info) => {
          const rowData = info.row.original as any;
          const managersCount = rowData?.managers
            ? rowData?.managers.length
            : 0;
          const membersCount = rowData?.memberCount ? rowData?.memberCount : 0;
          const subTeamsCount = rowData?.subTeams ? rowData.subTeams.length : 0;
             

          return (
            <Flex
              flexDirection="column"
              gap="2"
              width="100px"
              alignItems="flex-start"
            >
              <Text>{managersCount} Managers</Text>
              <Text>{membersCount} Members</Text>
              <Text>{subTeamsCount} Subteams</Text>
            </Flex>
          );
        },
        header: 'Members',
        size: 50,
        meta: {
          isNumeric: true,
        },
      }),
      columnHelper.accessor('setupStates', {
        cell: (info) => (
          <UnorderedList listStyleType={'none'}>
            <ListItem display={'flex'} gap={1}>
              {info.getValue().Communication ? (
                <Image src={Present}></Image>
              ) : (
                <Image src={NotPresent}></Image>
              )}
              Communication
            </ListItem>
            <ListItem display={'flex'} gap={1}>
              {info.getValue().Dora ? (
                <Image src={Present}></Image>
              ) : (
                <Image src={NotPresent}></Image>
              )}
              DORA
            </ListItem>
            <ListItem display={'flex'} gap={1}>
              {info.getValue().Issue ? (
                <Image src={Present}></Image>
              ) : (
                <Image src={NotPresent}></Image>
              )}
              Issue
            </ListItem>
            <ListItem display={'flex'} gap={1}>
              {info.getValue().Git ? (
                <Image src={Present}></Image>
              ) : (
                <Image src={NotPresent}></Image>
              )}
              Git
            </ListItem>
          </UnorderedList>
        ),
        header: 'Config Status',
      }),

      columnHelper.accessor('actions', {
        cell: (info) => (
          <Flex>
            <Tooltip label="Edit" hasArrow>
              <IconButton
                aria-label="edit"
                bg="transparent"
                size="sm"
                color="text.secondary"
                icon={<MdOutlineEdit size={16} />}
                position={'static'}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  navigate(`/settings/teams/${info.row.original?.name}`);
                }}
              />
            </Tooltip>

            <ConfirmButton
              buttonText="Delete"
              showIcon
              bodyText={`Do you really want to delete this team - ${info.row.original?.name}?`}
              headerText="Are you sure?"
              onSuccessAction={() => {
                if (info.row.original.subTeams.length >= 1) {
                  newToast({
                    message:
                      'Cannot delete top level team if sub teams available.',
                    status: 'error',
                  });
                } else {
                  handleDelete(info.row.original?.name);
                }
              }}
            />

            <Tooltip label="Add Member" hasArrow>
              <IconButton
                aria-label="edit"
                size="sm"
                bg="transparent"
                color="primary"
                icon={<MdPersonAddAlt size={16} />}
                position={'static'}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  navigate(`/settings/teams/${info.row.original?.name}`, {
                    state: { tab: 1 },
                  });
                }}
              />
            </Tooltip>
          </Flex>
        ),
        header: 'Actions',
      }),
    ],
    [teamsData?.dto]
  );

  const handleDelete = (name: string) => {
    setLoading(true);
    apiClient(`/v1/team/${localStorage.getItem('orgId')}/${name}`, {
      method: 'DELETE',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        authorization: `bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((res: any) => {
        Promise.all([
          queryClient.invalidateQueries([QUERY_KEYS.teams]),
          queryClient.invalidateQueries([TEAM_DETAILS_QUERY_KEYS.teamList]),
          queryClient.invalidateQueries(['teamMenu']),
        ]);

        newToast({
          message: `"${name}" Team has been deleted successfully.`,
          status: 'success',
        });
      })
      .catch((err: any) => {
        newToast({
          message:
            err?.message ?? `Some error occurred while deleting ${name}.`,
          status: 'error',
        });
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <>
      <DataGrid
        page="team"
        teamLength={teamLength}
        plan={plan}
        appState={appState}
        showLoader={teamsDataLoading}
        columns={columns}
        data={rows}
        maxH="40rem"
        sticky="firstCol"
      />
      {(loading || teamsDataLoading) && <Loader />}
    </>
  );
};

export default TeamView;
