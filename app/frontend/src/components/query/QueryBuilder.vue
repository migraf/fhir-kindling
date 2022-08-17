<script lang="ts">
import {getResourceNames} from '../../domains/resource/api';
import {computed, reactive, ref} from "vue";
import FilterBuilder from "./filter/FilterBuilder.vue";
import SearchBar from "../common/SearchBar.vue";
import QueryStatus from "./QueryStatus.vue";
import {FieldParameter, IncludeParameter, ReverseChainParameter} from "../../domains/query/type";
import {urlResourceField} from "../../domains/query/api";
import QueryOverview from "./QueryOverview.vue";

export default {
  components: {QueryOverview, QueryStatus, SearchBar, FilterBuilder},
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

    function handleEdit() {
      console.log("handleEdit");
      state.selectedResource = '';
      state.status = 'initialized';
      state.fieldParameters = [];
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
      handleRemoveFilter
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
    />

  </div>
</template>

<style scoped>

</style>
