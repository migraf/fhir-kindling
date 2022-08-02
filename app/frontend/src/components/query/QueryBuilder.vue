<script lang="ts">
import { getResourceNames } from '../../domains/resource/api';
import {ref} from "vue";
import ResourceSelector from "../resource/ResourceSelector.vue";

export default {
  components: {ResourceSelector},
  async setup() {
    const loading = ref(false);
    const resourceResponse = await getResourceNames();
    const resourceNames = resourceResponse

    return {
      loading,
      resourceNames,
    };
  },
}

</script>

<template>
  <div>
    <ResourceSelector
        :resource-names="resourceNames"
    />
  </div>
</template>

<style scoped>

</style>
