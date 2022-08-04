<script lang="ts">
import {getResourceFields, getResourceNames} from '../../domains/resource/api';
import {computed, reactive, ref} from "vue";
import ResourceQuery from "./ResourceQuery.vue";
import SearchBar from "../shared/SearchBar.vue";
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
    })

    async function handleSelected(resource: string) {
      console.log("handleSelected", resource);
      state.selectedResource = resource;
      state.status = 'resourceSelected';
    }

    const queryString = computed(() => {
      return `/${state.selectedResource}?`;
    });

    return {
      queryString,
      state,
      loading,
      resourceNames,
      handleSelected,
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
    />
    <ResourceQuery
        v-if="state.selectedResource"
        :resource="state.selectedResource"
    />

  </div>
</template>

<style scoped>

</style>
