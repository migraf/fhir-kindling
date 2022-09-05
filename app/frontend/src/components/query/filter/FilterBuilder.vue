<script lang="ts">
import {reactive, ref, defineEmits} from "vue";
import {getResourceFields} from "../../../domains/resource/api";
import FilterForm from "./FilterForm.vue";
import FilterOverview from "./FilterOverview.vue";
import {FieldParameter, Operators} from "../../../domains/query/type";
import {ResourceField} from "../../../domains/resource/type";

export default {
  components: {FilterForm, FilterOverview},
  props: {
    resource: String,
    fields: Array<FieldParameter>
  },
  emits: [
    "addFilter"
  ],
  async setup(props: any, context: any) {
    const loading = ref(false);
    const fieldResponse = await getResourceFields(props.resource);
    const defaultFilters = ["resource_type"]
    console.log("prop fields", props.resourceFields);
    const state = reactive({
      selectedField: '',
      resourceFields: fieldResponse.fields,
      filters: {
        extensions: true,
        default: true,
      },
      fieldParameters: props.fields === undefined ? Array<FieldParameter>() : props.fields,
      add: true,
    })

    async function handleSelected(item: string) {
      console.log("handleSelected", item);
      state.selectedField = item;
    }

    function handleAddFilter(filter: FieldParameter) {
      console.log("handleAddFilter", filter);
      // state.fieldParameters.push(filter);
      context.emit("addFilter", filter);
      state.add = false;
    }

    function handleRemoveFilter(filter: FieldParameter) {
      console.log("handleRemoveFilter filter builder", filter);
      context.emit("removeFilter", filter);

    }
    return {
      state,
      loading,
      fieldResponse,
      defaultFilters,
      handleSelected,
      handleAddFilter,
      handleRemoveFilter
    };
  },
}
</script>

<template>
  <div class="flex flex-col mt-4">
    <FilterOverview
        v-if="state.fieldParameters.length > 0"
        :filters="state.fieldParameters"
        @removeFilter="handleRemoveFilter"
    />
    <div
        v-if="!state.add"
        class="flex flex-grow justify-center mt-2"
        @click="state.add = true"

    >
      <button
          class="bg-blue-700 text-white rounded-lg p-2 justify-items-center"
      >
        <font-awesome-icon icon="fa-solid fa-plus" />
        Add Filter
      </button>
    </div>
    <FilterForm
        v-if="state.add"
        :resource="resource"
        :fields="state.resourceFields"
        @addFilter="handleAddFilter"
    >

    </FilterForm>
  </div>
</template>

<style scoped>

</style>
