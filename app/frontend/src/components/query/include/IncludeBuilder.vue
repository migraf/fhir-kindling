<script setup lang="ts">
import {computed, ref, reactive, onMounted } from 'vue'
import {FieldParameter, IncludeParameter, ReverseChainParameter} from "../../../domains/query/type";
import IncludeForm from "./IncludeForm.vue";
import IncludeOverview from "./IncludeOverview.vue";

interface Props {
  includeParams: IncludeParameter[];
  resourceNames: string[];
}

const props = defineProps<Props>()

const emits = defineEmits(["removeInclude", "addInclude"]);

function handleAddInclude(parameter: IncludeParameter) {
  console.log("handleAddInclude query summary", parameter);
  emits("addInclude", parameter);
}

function handleRemoveInclude(parameter: IncludeParameter) {
  console.log("handleRemoveInclude query summary", parameter);
  emits("removeInclude", parameter);
}

</script>

<template>
  <div>
    <IncludeOverview
        :include-params="props.includeParams"
        @removeInclude="handleRemoveInclude"
    />
    <IncludeForm
        :resource-names="props.resourceNames"
        @add-include="handleAddInclude"
    />
  </div>
</template>


<style scoped>

</style>
