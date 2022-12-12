<script setup lang="ts">
import {computed, reactive, ref} from "vue";
import {QueryResponse} from "../../../domains/query/type";
import SideBar from "./SideBar.vue";
import ResultDisplay from "./ResultDisplay.vue";

interface Props {
  result: QueryResponse;
}
const props = defineProps<Props>()

const state = reactive({
  selectedResource: "",
})

function handleSelectResource(resource: string) {
  state.selectedResource = resource;
  console.log(props.result.resources)
}

const selectedResults = computed(() => {
  if (state.selectedResource === "") {
    return props.result.resources[0];
  }
  return props.result.resources.filter((resource) => resource.resource === state.selectedResource)[0];
})

</script>

<template>
  <div class="flex flex-row">
    <div class="flex-row">
      <SideBar
          v-if="props.result !== null"
          :resources="props.result.resources"
          @selectResource="handleSelectResource"
      />
    </div>
    <ResultDisplay
        class="ml-4 mt-2"
        v-if="state.selectedResource !== ''"
        :result="selectedResults"
    />
  </div>
</template>


<style scoped>

</style>
