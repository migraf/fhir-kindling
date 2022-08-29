<script setup lang="ts">
import {computed, ref, reactive, onMounted, defineEmits} from 'vue'
import {FieldParameter, IncludeParameter, ReverseChainParameter} from "../../domains/query/type";
import FilterOverview from "./filter/FilterOverview.vue";
import IncludeOverview from "./include/IncludeOverview.vue";

interface Props {
  fieldParams?: FieldParameter[];
  includeParams?: IncludeParameter[];
  chainParams?: ReverseChainParameter[];
}

const props = defineProps<Props>()

const emits = defineEmits(["removeFilter", "removeInclude"])

function handleRemoveFilter(filter: FieldParameter) {
  console.log("handleRemoveFilter query summary", filter);
  emits("removeFilter", filter);
}

function handleRemoveInclude(parameter: IncludeParameter) {
  console.log("handleRemoveInclude query summary", parameter);
  emits("removeInclude", parameter);
}

</script>

<template>
  <div class="flex flex-col flex-grow mt-4">
    <div class="text-gray-100 text-xl">
      Field Parameters:
    </div>
    <FilterOverview
        v-if="props.fieldParams !== undefined && props.fieldParams.length > 0"
        :filters="props.fieldParams"
        class="mt-2"
        @removeFilter="handleRemoveFilter"
    />
    <div
        v-else
        class="my-2"
    >
      None
    </div>
    <div class="text-gray-100 text-xl">
      Include Parameters:
    </div>
    <IncludeOverview
        v-if="props.includeParams !== undefined && props.includeParams.length > 0"
        class="mb-2"
        :include-params="props.includeParams"
        @removeInclude="handleRemoveInclude"
    />

    <div
        v-else
        class="mb-2"
    >
      None
    </div>
    <div class="text-gray-100 text-xl mb-2">
      Chain Parameters:
    </div>
    <div
        class="mb-2"
    >
      Chains
    </div>



  </div>

</template>




<style scoped>

</style>
