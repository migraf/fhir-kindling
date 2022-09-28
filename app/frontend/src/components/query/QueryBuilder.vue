<script lang="ts">
import {getResourceNames} from '../../domains/resource/api';
import {computed, reactive, ref} from "vue";
import FilterBuilder from "./filter/FilterBuilder.vue";
import SearchBar from "../common/SearchBar.vue";
import QueryStatus from "./QueryStatus.vue";
import {
  FieldParameter,
  IncludeParameter,
  ReverseChainParameter,
  QueryParameters,
  QueryResponse
} from "../../domains/query/type";
import {urlResourceField, urlIncludeParameter, runQuery} from "../../domains/query/api";
import QueryOverview from "./QueryOverview.vue";
import IncludeBuilder from "./include/IncludeBuilder.vue";
import QueryResults from "./results/QueryResults.vue";

export default {
  components: {QueryResults, IncludeBuilder, QueryOverview, QueryStatus, SearchBar, FilterBuilder},
  async setup() {
    const loading = ref(false);
    const resourceNames = await getResourceNames()


    const state = reactive({
      selectedResource: '',
      resourceFields: [],
      status: 'initialized',
      selectedTab: 'overview',
      fieldParameters: Array<FieldParameter>(),
      includeParameters: Array<IncludeParameter>(),
      chainParameters: Array<ReverseChainParameter>(),
      response: {},
    })

    async function handleSelected(resource: string) {
      console.log("handleSelected", resource);
      state.selectedResource = resource;
      state.status = 'resourceSelected';
    }

    const queryString = computed(() => {

      let query = `/${state.selectedResource}?`;
      if (state.fieldParameters.length > 0) {
        query += `${state.fieldParameters.map(param => urlResourceField(param)).join('&')}`;
      }

      if (state.includeParameters.length > 0) {
        if (state.fieldParameters.length > 0) {
          query += '&';
        }
        query += `${state.includeParameters.map(param => urlIncludeParameter(param)).join('&')}`;
      }
      return query;
    });

    function handleTabSelect(tab: string) {
      console.log("handleTabSelect", tab);
      state.selectedTab = tab;
    }

    async function handleAddFilter(filter: FieldParameter) {
      console.log("Query builder add filter", filter);
      state.fieldParameters.push(filter);
    }

    function handleRemoveFilter(filter: FieldParameter) {
      console.log("Query builder remove filter", filter);
      state.fieldParameters = state.fieldParameters.filter(
          param => {
            return param.field !== filter.field && param.operator !== filter.operator && param.value !== filter.value;
          });
    }

    function handleAddInclude(include: IncludeParameter) {
      console.log("Query builder add include", include);
      state.includeParameters.push(include);
    }

    function handleRemoveInclude(include: IncludeParameter) {
      console.log("Query builder remove include", include);
      state.includeParameters = state.includeParameters.filter(
          param => {
            return param.resource !== include.resource && param.search_param !== include.search_param;
          });
    }

    function handleEdit() {
      console.log("handleEdit");
      state.selectedResource = '';
      state.status = 'initialized';
      state.fieldParameters = [];
    }

    async function handleRunQuery() {
      console.log("handleRunQuery");


      const queryParameters = {
        resource: state.selectedResource,
        resource_parameters: state.fieldParameters,
        include_parameters: state.includeParameters,
        has_parameters: state.chainParameters
      } as QueryParameters;

      state.selectedTab = "results";
      state.status = 'queryRunning';

      state.response = await runQuery(queryParameters);
      state.status = 'queryFinished';

    }

    return {
      queryString,
      state,
      loading,
      resourceNames,
      handleSelected,
      handleTabSelect,
      handleAddFilter,
      handleEdit,
      handleRemoveFilter,
      handleAddInclude,
      handleRemoveInclude,
      handleRunQuery
    };
  },
  computed
}

</script>

<template>
  <div class="p-2">
    <SearchBar
        v-if="state.status === 'initialized'"
        :items="resourceNames"
        @selected="handleSelected"
        :hint="'Select a resource...'"
    />
    <QueryStatus
        v-if="state.status !== 'initialized'"
        :resource="state.selectedResource"
        :query="queryString"
        :status="state.status"
        @edit-resource="handleEdit"
        @select-tab="handleTabSelect"
        :filters="state.fieldParameters"
        :includes="state.includeParameters"
        @runQuery="handleRunQuery"

    />
    <FilterBuilder
        v-if="state.selectedResource && state.selectedTab === 'filters'"
        :resource="state.selectedResource"
        :fields="state.fieldParameters"
        @addFilter="handleAddFilter"
        @removeFilter="handleRemoveFilter"
    />
    <QueryOverview
        v-if="state.selectedResource && state.selectedTab === 'overview'"
        :field-params="state.fieldParameters"
        :include-params="state.includeParameters"
        :chain-params="state.chainParameters"
        @removeFilter="handleRemoveFilter"
        @removeInclude="handleRemoveInclude"
    />
    <IncludeBuilder
        v-if="state.selectedResource && state.selectedTab === 'includes'"
        :resource="state.selectedResource"
        :fields="state.fieldParameters"
        :resource-names="resourceNames"
        :include-params="state.includeParameters"
        @addInclude="handleAddInclude"
        @removeInclude="handleRemoveInclude"
    />
    <QueryResults
        v-if="state.selectedResource && state.selectedTab === 'results'"
        :result="state.response"
    />


  </div>
</template>

<style scoped>

</style>
