<script setup lang="ts">
import {reactive, ref} from "vue";
import {ResourceField} from "../../../domains/resource/type";
import {Operators} from "../../../domains/query/type";
import SearchBar from "../../common/SearchBar.vue";
import OperatorSelect from "../OperatorSelect.vue";

interface Props {
  resource: string;
  fields: ResourceField[];
}

const props = defineProps<Props>()

const state = reactive({
  selectedField: '',
  filters: {
    extensions: true,
    default: true,
  },
  operator: 'eq',
  value: '',
})

function handleFieldSelect(item: string) {
  console.log("handleFieldSelect", item);
  state.selectedField = item;
}

function handleOperatorSelect(operator: Operators) {
  console.log("operatorSelected", operator);
  state.operator = operator.valueOf();
}

const emits = defineEmits(["addFilter"]);

function addFilter() {
  console.log("addFilter", state.selectedField, state.operator, state.value);
  emits("addFilter", {
    field: state.selectedField,
    operator: state.operator,
    value: state.value,
  });
}

</script>

<template>
  <div class="flex grid gap-2 grid-cols-8 flex-grow">
    <div class="col-span-3">
      <SearchBar
          :items="fields"
          @selected="handleFieldSelect"
          :hint="'Select a field...'"
          :keys="['name', 'description', 'title']"
          v-slot:default="{item}"
      >
        <div>
          {{ item.name }}
        </div>
      </SearchBar>
    </div>
    <div class="">
      <operator-select
          @operatorSelected="handleOperatorSelect"
      />
    </div>
    <div class="col-span-3">
      <input
          type="text"
          id="query-value"
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500
          focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
          dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Enter search value..."
          v-model="state.value"
          required
      >
    </div>
    <div>
      <button
          type="submit"
          class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
          @click="addFilter"
      >
        Add Filter
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>
