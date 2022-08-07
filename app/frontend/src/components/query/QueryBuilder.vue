<script lang="ts">
import {getResourceFields, getResourceNames} from '../../domains/resource/api';
import {computed, reactive, ref} from "vue";
import ResourceQuery from "./FilterBuilder.vue";
import SearchBar from "../common/SearchBar.vue";
import QueryStatus from "./QueryStatus.vue";

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
    })

    async function handleSelected(resource: string) {
      console.log("handleSelected", resource);
      state.selectedResource = resource;
      state.status = 'resourceSelected';
    }

    const queryString = computed(() => {
      return `/${state.selectedResource}?`;
    });

    function handleTabSelect(tab: string) {
      console.log("handleTabSelect", tab);
      state.selectedTab = tab;
    }

    return {
      queryString,
      state,
      loading,
      resourceNames,
      handleSelected,
      handleTabSelect,
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
    />
    <ResourceQuery
        v-if="state.selectedResource && state.selectedTab === 'filters'"
        :resource="state.selectedResource"
    />

  </div>
</template>

<style scoped>

</style>
