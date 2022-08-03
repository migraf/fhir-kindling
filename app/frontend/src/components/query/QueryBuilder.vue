<script lang="ts">
import {getResourceFields, getResourceNames} from '../../domains/resource/api';
import {reactive, ref} from "vue";
import ResourceSelector from "../shared/SearchBar.vue";

export default {
  components: {ResourceSelector},
  async setup() {
    const loading = ref(false);
    const resourceResponse = await getResourceNames();
    const resourceNames = resourceResponse

    const state = reactive({
      selectedResource: '',
    })

    function handleSelected(resource: string) {
      console.log("handleSelected", resource);
      state.selectedResource = resource;
    }

    return {
      state,
      loading,
      resourceNames,
      handleSelected,
    };
  },
}

</script>

<template>
  <div class="p-2">
    <ResourceSelector
        :resource-names="resourceNames"
        @selected="handleSelected"
    />
    {{state.selectedResource}}

  </div>
</template>

<style scoped>

</style>
