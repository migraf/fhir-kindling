<script lang="ts">
import {reactive, ref, defineEmits} from "vue";
import {getResourceFields} from "../../../domains/resource/api";
import FilterForm from "./FilterForm.vue";
import FilterOverview from "./FilterOverview.vue";
import {FieldParameter} from "../../../domains/query/type";

export default {
  components: {FilterForm, FilterOverview},
  props: {
    resource: String
  },
  emits: [
    "addFilter"
  ],
  async setup(props: any, context: any) {
    const loading = ref(false);
    const fieldResponse = await getResourceFields(props.resource);
    const defaultFilters = ["resource_type"]
    const state = reactive({
      selectedField: '',
      resourceFields: fieldResponse.fields,
      filters: {
        extensions: true,
        default: true,
      },
      fieldParameters: Array<FieldParameter>(),
      add: true,
    })
    async function handleSelected(item: string) {
      console.log("handleSelected", item);
      state.selectedField = item;
    }

    function handleAddFilter(filter: FieldParameter) {
      console.log("handleAddFilter", filter);
      state.fieldParameters.push(filter);
      context.emit("addFilter", filter);
      state.add = false;
    }
    return {
      state,
      loading,
      fieldResponse,
      defaultFilters,
      handleSelected,
      handleAddFilter,
    };
  },
}
</script>

<template>
  <div class="flex flex-col">
    <h5>Todo</h5>
  </div>
  <FilterForm
      v-if="state.add"
      :resource="resource"
      :fields="state.resourceFields"
      @addFilter="handleAddFilter"
  >

  </FilterForm>
</template>

<style scoped>

</style>
