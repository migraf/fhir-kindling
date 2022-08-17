<script lang="ts">
import {getResourceFields, getResourceNames} from '../../domains/resource/api';
import {computed, reactive, ref} from "vue";
import ResourceQuery from "./filter/FilterBuilder.vue";
import SearchBar from "../common/SearchBar.vue";
import QueryStatus from "./QueryStatus.vue";
import {FieldParameter} from "../../domains/query/type";
import {urlResourceField} from "../../domains/query/api";

export default {
  components: {QueryStatus, SearchBar, ResourceQuery},
  async setup() {
    const loading = ref(false);
    const resourceResponse = await getResourceNames();
    const resourceNames = resourceResponse


    const state = reactive({
      selectedResource: '',
      resourceFields: [],
      status: 'initialized',
      selectedTab: 'summary',
      fieldParameters: Array<FieldParameter>(),
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

    return {
      queryString,
      state,
      loading,
      resourceNames,
      handleSelected,
      handleTabSelect,
      handleAddFilter
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
        @edit-resource="state.status = 'initialized'"
        @select-tab="handleTabSelect"
        :filters="state.fieldParameters"
    />
    <ResourceQuery
        v-if="state.selectedResource && state.selectedTab === 'filters'"
        :resource="state.selectedResource"
        @addFilter="handleAddFilter"
    />

  </div>
</template>

<style scoped>

</style>
