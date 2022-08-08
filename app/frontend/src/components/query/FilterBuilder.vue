<script lang="ts">
import {reactive, ref} from "vue";
import {getResourceFields} from "../../domains/resource/api";
import FilterForm from "./FilterForm.vue";
export default {
  components: {FilterForm},
  props: {
    resource: String
  },
  async setup(props: any) {
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
    })
    async function handleSelected(item: string) {
      console.log("handleSelected", item);
      state.selectedField = item;
    }
    return {
      state,
      loading,
      fieldResponse,
      defaultFilters,
      handleSelected,
    };
  },
}
</script>

<template>
  <FilterForm
      :resource="resource"
      :fields="state.resourceFields"
      class="mt-4"
  >

  </FilterForm>
</template>

<style scoped>

</style>
