#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import pytest

from cmk.agent_based.v2 import (
    CheckResult,
    DiscoveryResult,
    get_value_store,
    Metric,
    Result,
    Service,
    State,
    StringTable,
)
from cmk.plugins.lib.wmi import parse_wmi_table
from cmk.plugins.msexch.agent_based.msexch_isstore import (
    check_msexch_isstore,
    inventory_msexch_isstore,
    Params,
)

_AGENT_OUTPUT = [
    [
        "AdministrativeRPCrequestsPersec",
        "AdminRPCRequests",
        "Caption",
        "Description",
        "DirectoryAccessLDAPSearchesPersec",
        "Frequency_Object",
        "Frequency_PerfTime",
        "Frequency_Sys100NS",
        "JetLogRecordBytesPersec",
        "JetLogRecordsPersec",
        "JetPagesModifiedPersec",
        "JetPagesPrereadPersec",
        "JetPagesReadPersec",
        "JetPagesReferencedPersec",
        "JetPagesRemodifiedPersec",
        "LazyindexescreatedPersec",
        "LazyindexesdeletedPersec",
        "LazyindexfullrefreshPersec",
        "LazyindexincrementalrefreshPersec",
        "MessagescreatedPersec",
        "MessagesdeletedPersec",
        "MessagesopenedPersec",
        "MessagesupdatedPersec",
        "Name",
        "PropertypromotionsPersec",
        "RPCAverageLatency",
        "RPCAverageLatency_Base",
        "RPCBytesReceivedPersec",
        "RPCBytesSentPersec",
        "RPCOperationsPersec",
        "RPCPacketsPersec",
        "RPCRequests",
        "Timestamp_Object",
        "Timestamp_PerfTime",
        "Timestamp_Sys100NS",
    ],
    [
        "13203303",
        "0",
        "",
        "",
        "61388",
        "0",
        "1953125",
        "10000000",
        "614653228",
        "12092743",
        "49049",
        "826",
        "312",
        "53440863",
        "8506178",
        "3",
        "24",
        "3",
        "838",
        "80486",
        "23006",
        "101226",
        "23140",
        "_total",
        "0",
        "1903888",
        "3908424",
        "1040",
        "400087174",
        "6138327",
        "3908424",
        "1145789",
        "0",
        "6743176285319",
        "130951777565340000",
    ],
]

_AGENT_OUTPUT_REGRESSION_01 = [
    [
        "Activemailboxes",
        "AverageKeywordStatsSearchExecutionTime",
        "AverageKeywordStatsSearchExecutionTime_Base",
        "AverageMultiMailboxSearchFailed",
        "AverageMultiMailboxSearchFailed_Base",
        "AverageMultiMailboxSearchQueryLength",
        "AverageMultiMailboxSearchQueryLength_Base",
        "AverageMultiMailboxSearchtimespentinFullTextIndex",
        "AverageMultiMailboxSearchtimespentinFullTextIndex_Base",
        "AverageMultiMailboxSearchtimespentinStorecalls",
        "AverageMultiMailboxSearchtimespentinStorecalls_Base",
        "AveragenumberofKeywordsinMultiMailboxSearch",
        "AveragenumberofKeywordsinMultiMailboxSearch_Base",
        "AverageSearchExecutionTime",
        "AverageSearchExecutionTime_Base",
        "Averagesearchresultsperquery",
        "Averagesearchresultsperquery_Base",
        "CachedeletesintheAddressInfocachePersec",
        "CachedeletesintheDatabaseInfocachePersec",
        "CachedeletesintheDistributionListMembershipcachePersec",
        "CachedeletesintheForeignAddressInfocachePersec",
        "CachedeletesintheForeignMailboxInfocachePersec",
        "CachedeletesintheIncompleteAddressInfocachePersec",
        "CachedeletesintheLogicalIndexcachePersec",
        "CachedeletesintheMailboxInfocachePersec",
        "CachedeletesintheOrganizationContainercachePersec",
        "CachehitsintheAddressInfocachePersec",
        "CachehitsintheDatabaseInfocachePersec",
        "CachehitsintheDistributionListMembershipcachePersec",
        "CachehitsintheForeignAddressInfocachePersec",
        "CachehitsintheForeignMailboxInfocachePersec",
        "CachehitsintheIncompleteAddressInfocachePersec",
        "CachehitsintheLogicalIndexcachePersec",
        "CachehitsintheMailboxInfocachePersec",
        "CachehitsintheOrganizationContainercachePersec",
        "CacheinsertsintheAddressInfocachePersec",
        "CacheinsertsintheDatabaseInfocachePersec",
        "CacheinsertsintheDistributionListMembershipcachePersec",
        "CacheinsertsintheForeignAddressInfocachePersec",
        "CacheinsertsintheForeignMailboxInfocachePersec",
        "CacheinsertsintheIncompleteAddressInfocachePersec",
        "CacheinsertsintheLogicalIndexcachePersec",
        "CacheinsertsintheMailboxInfocachePersec",
        "CacheinsertsintheOrganizationContainercachePersec",
        "CachelookupsintheAddressInfocachePersec",
        "CachelookupsintheDatabaseInfocachePersec",
        "CachelookupsintheDistributionListMembershipcachePersec",
        "CachelookupsintheForeignAddressInfocachePersec",
        "CachelookupsintheForeignMailboxInfocachePersec",
        "CachelookupsintheIncompleteAddressInfocachePersec",
        "CachelookupsintheLogicalIndexcachePersec",
        "CachelookupsintheMailboxInfocachePersec",
        "CachelookupsintheOrganizationContainercachePersec",
        "CachemissesintheAddressInfocachePersec",
        "CachemissesintheDatabaseInfocachePersec",
        "CachemissesintheDistributionListMembershipcachePersec",
        "CachemissesintheForeignAddressInfocachePersec",
        "CachemissesintheForeignMailboxInfocachePersec",
        "CachemissesintheIncompleteAddressInfocachePersec",
        "CachemissesintheLogicalIndexcachePersec",
        "CachemissesintheMailboxInfocachePersec",
        "CachemissesintheOrganizationContainercachePersec",
        "Caption",
        "DatabaseLevelMaintenancesPersec",
        "DatabaseState",
        "Description",
        "FolderscreatedPersec",
        "FoldersdeletedPersec",
        "FoldersopenedPersec",
        "Frequency_Object",
        "Frequency_PerfTime",
        "Frequency_Sys100NS",
        "IntegrityCheckDropBusyJobs",
        "IntegrityCheckFailedJobs",
        "IntegrityCheckPendingJobs",
        "IntegrityCheckTotalJobs",
        "LastMaintenanceItemRequestedAge",
        "Lazyindexchunkedpopulations",
        "LazyindexescreatedPersec",
        "LazyindexesdeletedPersec",
        "LazyindexfullrefreshPersec",
        "LazyindexincrementalrefreshPersec",
        "LazyindexinvalidationduetolocaleversionchangePersec",
        "LazyindexinvalidationPersec",
        "Lazyindexnonchunkedpopulations",
        "Lazyindexpopulationsfromindex",
        "Lazyindexpopulationswithouttransactionpulsing",
        "Lazyindextotalpopulations",
        "LostDiagnosticEntries",
        "MailboxesWithMaintenanceItems",
        "MailboxKeyDecryptAverageLatency",
        "MailboxKeyDecryptAverageLatency_Base",
        "MailboxKeyDecryptsPersec",
        "MailboxKeyEncryptsPersec",
        "MailboxLevelMaintenanceItems",
        "MailboxLevelMaintenancesPersec",
        "MAPIMessagesCreatedPersec",
        "MAPIMessagesModifiedPersec",
        "MAPIMessagesOpenedPersec",
        "MessagescreatedPersec",
        "MessagesdeletedPersec",
        "MessagesDeliveredPersec",
        "MessagesopenedPersec",
        "MessagesSubmittedPersec",
        "MessagesupdatedPersec",
        "MultiMailboxKeywordStatsSearchPersec",
        "MultiMailboxPreviewSearchPersec",
        "MultiMailboxSearchFullTextIndexQueryPersec",
        "Name",
        "NonrecursivefolderhierarchyreloadsPersec",
        "Numberofactivebackgroundtasks",
        "NumberofactiveWLMLogicalIndexmaintenancetablemaintenances",
        "NumberofmailboxesmarkedforWLMLogicalIndexmaintenancetablemaintenance",
        "NumberofprocessingLogicalIndexmaintenancetasks",
        "NumberofscheduledLogicalIndexmaintenancetasks",
        "PercentRPCRequests",
        "PercentRPCRequests_Base",
        "ProcessID",
        "PropertypromotionmessagesPersec",
        "PropertypromotionsPersec",
        "PropertyPromotionTasks",
        "QuarantinedComponentCount",
        "QuarantinedMailboxCount",
        "QuarantinedSchemaUpgraderCount",
        "QuarantinedUserAccessibleMailboxCount",
        "RecursivefolderhierarchyreloadsPersec",
        "RPCAverageLatency",
        "RPCAverageLatency_Base",
        "RPCOperationsPersec",
        "RPCPacketsPersec",
        "RPCPoolContextHandles",
        "RPCPoolParkedAsyncNotificationCalls",
        "RPCPoolPools",
        "RPCRequests",
        "ScheduledISIntegDetectedCount",
        "ScheduledISIntegFixedCount",
        "ScheduledISIntegPersec",
        "ScopeKeyReadAverageLatency",
        "ScopeKeyReadAverageLatency_Base",
        "ScopeKeyReadsPersec",
        "SearchPersec",
        "SearchresultsPersec",
        "SizeofAddressInfocache",
        "SizeofDatabaseInfocache",
        "SizeofDistributionListMembershipcache",
        "SizeofForeignAddressInfocache",
        "SizeofForeignMailboxInfocache",
        "SizeofIncompleteAddressInfocache",
        "SizeofLogicalIndexcache",
        "SizeofMailboxInfocache",
        "SizeofOrganizationContainercache",
        "SizeoftheexpirationqueuefortheAddressInfocache",
        "SizeoftheexpirationqueuefortheDatabaseInfocache",
        "SizeoftheexpirationqueuefortheDistributionListMembershipcache",
        "SizeoftheexpirationqueuefortheForeignAddressInfocache",
        "SizeoftheexpirationqueuefortheForeignMailboxInfocache",
        "SizeoftheexpirationqueuefortheIncompleteAddressInfocache",
        "SizeoftheexpirationqueuefortheLogicalIndexcache",
        "SizeoftheexpirationqueuefortheMailboxInfocache",
        "SizeoftheexpirationqueuefortheOrganizationContainercache",
        "SubobjectscleanedPersec",
        "SubobjectscreatedPersec",
        "SubobjectsdeletedPersec",
        "Subobjectsintombstone",
        "SubobjectsopenedPersec",
        "SuccessfulsearchPersec",
        "TimedEventsProcessed",
        "TimedEventsProcessedPersec",
        "TimedEventsProcessingFailures",
        "Timestamp_Object",
        "Timestamp_PerfTime",
        "Timestamp_Sys100NS",
        "TopMessagescleanedPersec",
        "Topmessagesintombstone",
        "TotalfailedmultimailboxkeywordstatisticsSearches",
        "TotalfailedmultimailboxPreviewSearches",
        "TotalMultiMailboxkeywordstatisticssearches",
        "Totalmultimailboxkeywordstatisticssearchestimedout",
        "TotalMultiMailboxpreviewsearches",
        "Totalmultimailboxpreviewsearchestimedout",
        "TotalMultiMailboxsearchesfailedduetoFullTextfailure",
        "TotalmultimailboxsearchesFullTextIndexQueryExecution",
        "Totalnumberofsuccessfulsearchqueries",
        "Totalobjectssizeintombstonebytes",
        "Totalsearches",
        "Totalsearchesinprogress",
        "Totalsearchqueriescompletedin005sec",
        "Totalsearchqueriescompletedin052sec",
        "Totalsearchqueriescompletedin1060sec",
        "Totalsearchqueriescompletedin210sec",
        "Totalsearchqueriescompletedin60sec",
    ],
    [
        "4",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "11705",
        "2038",
        "0",
        "0",
        "0",
        "0",
        "52",
        "7962",
        "0",
        "12671984",
        "18440396",
        "0",
        "0",
        "0",
        "0",
        "639930",
        "6127781",
        "0",
        "11708",
        "2038",
        "0",
        "0",
        "0",
        "0",
        "623",
        "7964",
        "0",
        "12684158",
        "18442669",
        "0",
        "12174",
        "8514",
        "0",
        "641176",
        "6136295",
        "0",
        "12174",
        "2273",
        "0",
        "12174",
        "8514",
        "0",
        "1246",
        "8514",
        "0",
        "",
        "11724",
        "1",
        "",
        "0",
        "0",
        "1220570",
        "0",
        "1953125",
        "10000000",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3",
        "24",
        "3",
        "838",
        "0",
        "0",
        "0",
        "2",
        "0",
        "3",
        "0",
        "1",
        "0",
        "0",
        "0",
        "0",
        "1",
        "11680",
        "40243",
        "51785",
        "66714",
        "80486",
        "23006",
        "28741",
        "101226",
        "11502",
        "23140",
        "0",
        "0",
        "0",
        "db3",
        "0",
        "0",
        "0",
        "1",
        "0",
        "0",
        "0",
        "50",
        "5716",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "284",
        "1977204",
        "4308720",
        "6138327",
        "4308720",
        "23304",
        "8",
        "11650",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3",
        "1",
        "0",
        "0",
        "0",
        "0",
        "8",
        "2",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "6743176366056",
        "130951777565810000",
        "23004",
        "2",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
    ],
    [
        "4",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "11705",
        "2038",
        "0",
        "0",
        "0",
        "0",
        "52",
        "7962",
        "0",
        "12671984",
        "18440397",
        "0",
        "0",
        "0",
        "0",
        "639930",
        "6127781",
        "0",
        "11708",
        "2039",
        "0",
        "0",
        "0",
        "0",
        "623",
        "7964",
        "0",
        "12684158",
        "18442671",
        "0",
        "12174",
        "8514",
        "0",
        "641176",
        "6136295",
        "0",
        "12174",
        "2274",
        "0",
        "12174",
        "8514",
        "0",
        "1246",
        "8514",
        "0",
        "",
        "11724",
        "1",
        "",
        "0",
        "0",
        "1220570",
        "0",
        "1953125",
        "10000000",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3",
        "24",
        "3",
        "838",
        "0",
        "0",
        "0",
        "2",
        "0",
        "3",
        "0",
        "1",
        "0",
        "0",
        "0",
        "0",
        "1",
        "11680",
        "40243",
        "51785",
        "66714",
        "80486",
        "23006",
        "28741",
        "101226",
        "11502",
        "23140",
        "0",
        "0",
        "0",
        "_total",
        "0",
        "0",
        "0",
        "1",
        "0",
        "0",
        "0",
        "50",
        "5716",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "284",
        "1977204",
        "4308720",
        "6138327",
        "4308720",
        "23336",
        "9",
        "11651",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3",
        "2",
        "0",
        "0",
        "0",
        "0",
        "8",
        "2",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "6743176366056",
        "130951777565810000",
        "23004",
        "2",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
    ],
]

_AGENT_OUTPUT_REGRESSION_02 = [
    [
        "Activemailboxes",
        "AverageKeywordStatsSearchExecutionTime",
        "AverageKeywordStatsSearchExecutionTime_Base",
        "AverageMultiMailboxSearchFailed",
        "AverageMultiMailboxSearchFailed_Base",
        "AverageMultiMailboxSearchQueryLength",
        "AverageMultiMailboxSearchQueryLength_Base",
        "AverageMultiMailboxSearchtimespentinFullTextIndex",
        "AverageMultiMailboxSearchtimespentinFullTextIndex_Base",
        "AverageMultiMailboxSearchtimespentinStorecalls",
        "AverageMultiMailboxSearchtimespentinStorecalls_Base",
        "AveragenumberofKeywordsinMultiMailboxSearch",
        "AveragenumberofKeywordsinMultiMailboxSearch_Base",
        "AverageSearchExecutionTime",
        "AverageSearchExecutionTime_Base",
        "Averagesearchresultsperquery",
        "Averagesearchresultsperquery_Base",
        "CachedeletesintheAddressInfocachePersec",
        "CachedeletesintheDatabaseInfocachePersec",
        "CachedeletesintheDistributionListMembershipcachePersec",
        "CachedeletesintheForeignAddressInfocachePersec",
        "CachedeletesintheForeignMailboxInfocachePersec",
        "CachedeletesintheIncompleteAddressInfocachePersec",
        "CachedeletesintheLogicalIndexcachePersec",
        "CachedeletesintheMailboxInfocachePersec",
        "CachedeletesintheOrganizationContainercachePersec",
        "CachehitsintheAddressInfocachePersec",
        "CachehitsintheDatabaseInfocachePersec",
        "CachehitsintheDistributionListMembershipcachePersec",
        "CachehitsintheForeignAddressInfocachePersec",
        "CachehitsintheForeignMailboxInfocachePersec",
        "CachehitsintheIncompleteAddressInfocachePersec",
        "CachehitsintheLogicalIndexcachePersec",
        "CachehitsintheMailboxInfocachePersec",
        "CachehitsintheOrganizationContainercachePersec",
        "CacheinsertsintheAddressInfocachePersec",
        "CacheinsertsintheDatabaseInfocachePersec",
        "CacheinsertsintheDistributionListMembershipcachePersec",
        "CacheinsertsintheForeignAddressInfocachePersec",
        "CacheinsertsintheForeignMailboxInfocachePersec",
        "CacheinsertsintheIncompleteAddressInfocachePersec",
        "CacheinsertsintheLogicalIndexcachePersec",
        "CacheinsertsintheMailboxInfocachePersec",
        "CacheinsertsintheOrganizationContainercachePersec",
        "CachelookupsintheAddressInfocachePersec",
        "CachelookupsintheDatabaseInfocachePersec",
        "CachelookupsintheDistributionListMembershipcachePersec",
        "CachelookupsintheForeignAddressInfocachePersec",
        "CachelookupsintheForeignMailboxInfocachePersec",
        "CachelookupsintheIncompleteAddressInfocachePersec",
        "CachelookupsintheLogicalIndexcachePersec",
        "CachelookupsintheMailboxInfocachePersec",
        "CachelookupsintheOrganizationContainercachePersec",
        "CachemissesintheAddressInfocachePersec",
        "CachemissesintheDatabaseInfocachePersec",
        "CachemissesintheDistributionListMembershipcachePersec",
        "CachemissesintheForeignAddressInfocachePersec",
        "CachemissesintheForeignMailboxInfocachePersec",
        "CachemissesintheIncompleteAddressInfocachePersec",
        "CachemissesintheLogicalIndexcachePersec",
        "CachemissesintheMailboxInfocachePersec",
        "CachemissesintheOrganizationContainercachePersec",
        "Caption",
        "DatabaseLevelMaintenancesPersec",
        "DatabaseState",
        "Description",
        "FolderscreatedPersec",
        "FoldersdeletedPersec",
        "FoldersopenedPersec",
        "Frequency_Object",
        "Frequency_PerfTime",
        "Frequency_Sys100NS",
        "IntegrityCheckDropBusyJobs",
        "IntegrityCheckFailedJobs",
        "IntegrityCheckPendingJobs",
        "IntegrityCheckTotalJobs",
        "LastMaintenanceItemRequestedAge",
        "Lazyindexchunkedpopulations",
        "LazyindexescreatedPersec",
        "LazyindexesdeletedPersec",
        "LazyindexfullrefreshPersec",
        "LazyindexincrementalrefreshPersec",
        "LazyindexinvalidationduetolocaleversionchangePersec",
        "LazyindexinvalidationPersec",
        "Lazyindexnonchunkedpopulations",
        "Lazyindexpopulationsfromindex",
        "Lazyindexpopulationswithouttransactionpulsing",
        "Lazyindextotalpopulations",
        "LostDiagnosticEntries",
        "MailboxesWithMaintenanceItems",
        "MailboxLevelMaintenanceItems",
        "MailboxLevelMaintenancesPersec",
        "MAPIMessagesCreatedPersec",
        "MAPIMessagesModifiedPersec",
        "MAPIMessagesOpenedPersec",
        "MessagescreatedPersec",
        "MessagesdeletedPersec",
        "MessagesDeliveredPersec",
        "MessagesopenedPersec",
        "MessagesSubmittedPersec",
        "MessagesupdatedPersec",
        "MultiMailboxKeywordStatsSearchPersec",
        "MultiMailboxPreviewSearchPersec",
        "MultiMailboxSearchFullTextIndexQueryPersec",
        "Name",
        "NonrecursivefolderhierarchyreloadsPersec",
        "Numberofactivebackgroundtasks",
        "NumberofactiveWLMLogicalIndexmaintenancetablemaintenances",
        "NumberofmailboxesmarkedforWLMLogicalIndexmaintenancetablemaintenance",
        "NumberofprocessingLogicalIndexmaintenancetasks",
        "NumberofscheduledLogicalIndexmaintenancetasks",
        "PercentRPCRequests",
        "PercentRPCRequests_Base",
        "ProcessID",
        "PropertypromotionmessagesPersec",
        "PropertypromotionsPersec",
        "PropertyPromotionTasks",
        "QuarantinedComponentCount",
        "QuarantinedMailboxCount",
        "QuarantinedSchemaUpgraderCount",
        "QuarantinedUserAccessibleMailboxCount",
        "RecursivefolderhierarchyreloadsPersec",
        "RPCAverageLatency",
        "RPCAverageLatency_Base",
        "RPCOperationsPersec",
        "RPCPacketsPersec",
        "RPCPoolContextHandles",
        "RPCPoolParkedAsyncNotificationCalls",
        "RPCPoolPools",
        "RPCRequests",
        "ScheduledISIntegDetectedCount",
        "ScheduledISIntegFixedCount",
        "ScheduledISIntegPersec",
        "SearchPersec",
        "SearchresultsPersec",
        "SizeofAddressInfocache",
        "SizeofDatabaseInfocache",
        "SizeofDistributionListMembershipcache",
        "SizeofForeignAddressInfocache",
        "SizeofForeignMailboxInfocache",
        "SizeofIncompleteAddressInfocache",
        "SizeofLogicalIndexcache",
        "SizeofMailboxInfocache",
        "SizeofOrganizationContainercache",
        "SizeoftheexpirationqueuefortheAddressInfocache",
        "SizeoftheexpirationqueuefortheDatabaseInfocache",
        "SizeoftheexpirationqueuefortheDistributionListMembershipcache",
        "SizeoftheexpirationqueuefortheForeignAddressInfocache",
        "SizeoftheexpirationqueuefortheForeignMailboxInfocache",
        "SizeoftheexpirationqueuefortheIncompleteAddressInfocache",
        "SizeoftheexpirationqueuefortheLogicalIndexcache",
        "SizeoftheexpirationqueuefortheMailboxInfocache",
        "SizeoftheexpirationqueuefortheOrganizationContainercache",
        "SubobjectscleanedPersec",
        "SubobjectscreatedPersec",
        "SubobjectsdeletedPersec",
        "Subobjectsintombstone",
        "SubobjectsopenedPersec",
        "SuccessfulsearchPersec",
        "Timestamp_Object",
        "Timestamp_PerfTime",
        "Timestamp_Sys100NS",
        "TopMessagescleanedPersec",
        "Topmessagesintombstone",
        "TotalfailedmultimailboxkeywordstatisticsSearches",
        "TotalfailedmultimailboxPreviewSearches",
        "TotalMultiMailboxkeywordstatisticssearches",
        "Totalmultimailboxkeywordstatisticssearchestimedout",
        "TotalMultiMailboxpreviewsearches",
        "Totalmultimailboxpreviewsearchestimedout",
        "TotalMultiMailboxsearchesfailedduetoFullTextfailure",
        "TotalmultimailboxsearchesFullTextIndexQueryExecution",
        "Totalnumberofsuccessfulsearchqueries",
        "Totalobjectssizeintombstonebytes",
        "Totalsearches",
        "Totalsearchesinprogress",
        "Totalsearchqueriescompletedin005sec",
        "Totalsearchqueriescompletedin052sec",
        "Totalsearchqueriescompletedin1060sec",
        "Totalsearchqueriescompletedin210sec",
        "Totalsearchqueriescompletedin60sec",
    ],
    [
        "9",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "2219184",
        "3736",
        "8803",
        "756",
        "0",
        "0",
        "0",
        "0",
        "8777",
        "10033",
        "0",
        "8331793",
        "16999241",
        "0",
        "0",
        "0",
        "0",
        "223497",
        "4021508",
        "0",
        "8811",
        "756",
        "0",
        "0",
        "0",
        "0",
        "9663",
        "10041",
        "0",
        "8344336",
        "17000070",
        "0",
        "12543",
        "10788",
        "0",
        "242823",
        "4032296",
        "0",
        "12543",
        "829",
        "0",
        "12543",
        "10788",
        "0",
        "19326",
        "10788",
        "0",
        "",
        "516",
        "1",
        "",
        "3736",
        "3736",
        "945803",
        "0",
        "2536125",
        "10000000",
        "0",
        "0",
        "0",
        "0",
        "3",
        "0",
        "7472",
        "7473",
        "3736",
        "612",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "3774",
        "15329",
        "15355",
        "232526",
        "28415",
        "2268",
        "9350",
        "234848",
        "13",
        "468",
        "0",
        "0",
        "0",
        "mailbox database 0356176343",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "50",
        "8084",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "631",
        "560849",
        "3606679",
        "5831463",
        "3606679",
        "146",
        "9",
        "67",
        "0",
        "0",
        "0",
        "0",
        "3736",
        "2219184",
        "8",
        "1",
        "0",
        "0",
        "0",
        "0",
        "0",
        "8",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "5264",
        "5257",
        "10514",
        "0",
        "5296",
        "3736",
        "0",
        "2844496046608",
        "131405402071970000",
        "2275",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3736",
        "0",
        "3736",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "0",
    ],
    [
        "9",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "2219184",
        "3736",
        "8803",
        "756",
        "0",
        "0",
        "0",
        "0",
        "8777",
        "10033",
        "0",
        "8331793",
        "16999243",
        "0",
        "0",
        "0",
        "0",
        "223497",
        "4021508",
        "0",
        "8811",
        "757",
        "0",
        "0",
        "0",
        "0",
        "9663",
        "10041",
        "0",
        "8344336",
        "17000073",
        "0",
        "12543",
        "10788",
        "0",
        "242823",
        "4032296",
        "0",
        "12543",
        "830",
        "0",
        "12543",
        "10788",
        "0",
        "19326",
        "10788",
        "0",
        "",
        "516",
        "1",
        "",
        "3736",
        "3736",
        "945803",
        "0",
        "2536125",
        "10000000",
        "0",
        "0",
        "0",
        "0",
        "3",
        "0",
        "7472",
        "7473",
        "3736",
        "612",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "3774",
        "15329",
        "15355",
        "232526",
        "28415",
        "2268",
        "9350",
        "234848",
        "13",
        "468",
        "0",
        "0",
        "0",
        "_total",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "50",
        "8084",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "631",
        "560849",
        "3606679",
        "5831463",
        "3606679",
        "178",
        "10",
        "68",
        "0",
        "0",
        "0",
        "0",
        "3736",
        "2219184",
        "8",
        "2",
        "0",
        "0",
        "0",
        "0",
        "0",
        "8",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "5264",
        "5257",
        "10514",
        "0",
        "5296",
        "3736",
        "0",
        "2844496046608",
        "131405402071970000",
        "2275",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "3736",
        "0",
        "3736",
        "0",
        "3736",
        "0",
        "0",
        "0",
        "0",
    ],
]


@pytest.mark.parametrize(
    "string_table, expected_result",
    [
        (
            _AGENT_OUTPUT,
            [
                Service(item="_total", parameters={}),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_01,
            [
                Service(item="_total", parameters={}),
                Service(item="db3", parameters={}),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_02,
            [
                Service(item="_total", parameters={}),
                Service(item="mailbox database 0356176343", parameters={}),
            ],
        ),
    ],
)
def test_parse_msexch_isstore(string_table: StringTable, expected_result: DiscoveryResult) -> None:
    section = parse_wmi_table(string_table)
    assert sorted(inventory_msexch_isstore(section)) == expected_result


@pytest.mark.usefixtures("initialised_item_state")
@pytest.mark.parametrize(
    "string_table, item, params, expected_result",
    [
        (
            _AGENT_OUTPUT,
            "_total",
            Params(
                store_latency_s=("no_levels", None),
                clienttype_latency_s=("no_levels", None),
                clienttype_requests=("no_levels", None),
            ),
            [
                Result(state=State.OK, summary="Average latency: 487 microseconds"),
                Metric("average_latency_s", 0.00048712422193702634),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_01,
            "_total",
            Params(
                store_latency_s=("no_levels", None),
                clienttype_latency_s=("no_levels", None),
                clienttype_requests=("no_levels", None),
            ),
            [
                Result(state=State.OK, summary="Average latency: 459 microseconds"),
                Metric("average_latency_s", 0.0004588843090291316),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_01,
            "db3",
            Params(
                store_latency_s=("fixed", (0.0004, 0.0005)),
                clienttype_latency_s=("no_levels", None),
                clienttype_requests=("no_levels", None),
            ),
            [
                Result(
                    state=State.WARN,
                    summary="Average latency: 459 microseconds (warn/crit at 400 microseconds/500 microseconds)",
                ),
                Metric("average_latency_s", 0.0004588843090291316, levels=(0.0004, 0.0005)),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_02,
            "_total",
            Params(
                store_latency_s=("no_levels", None),
                clienttype_latency_s=("no_levels", None),
                clienttype_requests=("no_levels", None),
            ),
            [
                Result(state=State.OK, summary="Average latency: 156 microseconds"),
                Metric("average_latency_s", 0.00015550288783670519),
            ],
        ),
        (
            _AGENT_OUTPUT_REGRESSION_02,
            "mailbox database 0356176343",
            Params(
                store_latency_s=("fixed", (0.0001, 0.0002)),
                clienttype_latency_s=("no_levels", None),
                clienttype_requests=("no_levels", None),
            ),
            [
                Result(
                    state=State.WARN,
                    summary="Average latency: 156 microseconds (warn/crit at 100 microseconds/200 microseconds)",
                ),
                Metric("average_latency_s", 0.00015550288783670519, levels=(0.0001, 0.0002)),
            ],
        ),
    ],
)
def test_check_msexch_isstore(
    string_table: StringTable,
    item: str,
    params: Params,
    expected_result: CheckResult,
) -> None:
    get_value_store().update({"RPCRequests_": (0.0, 1145789)})
    section = parse_wmi_table(string_table)
    assert list(check_msexch_isstore(item, params, section)) == expected_result
