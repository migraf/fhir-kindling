<script setup lang="ts">
import {computed, ref, reactive, onMounted} from 'vue'
import SearchBar from "../../common/SearchBar.vue";

interface Props {
  resourceNames: string[];
}

const props = defineProps<Props>()

const state = reactive({
  selectedResource: '',
  reverse: false,
  target: '',
  iterate: false,
  searchParam: '',
})

const emits = defineEmits(["addInclude"]);

function handleResourceSelect(resource: string) {
  console.log("handleResourceSelect - include: ", resource);
  state.selectedResource = resource;
}

function addIncludeParam() {
  console.log("includestate", state)
  console.log("addIncludeParam - include: ", state.selectedResource);
  emits(
      "addInclude",
      {
        resource: state.selectedResource,
        reverse: state.reverse,
        target: state.target,
        iterate: state.iterate,
        search_param: state.searchParam,
      }
  );
}

</script>

<template>
  <div class="flex flex-col">
    Include Form
    <div class="grid gap-2 grid-cols-8">
      <div class="col-span-3">
        <SearchBar
            :items="resourceNames"
            @selected="handleResourceSelect"
            :hint="'Select a resource to include...'"
        />

      </div>
      <div class="col-span-3">
        <div>
          <input
              type="text"
              id="reference-field"
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500
              focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
              dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="Enter reference param"
              v-model="state.searchParam"
              >
        </div>
      </div>
      <div>
        <div class="flex items-center mb-2">
          <input
              id="reverse-checkbox"
              :class="{
                'checked': state.reverse,
              }"

              v-model="state.reverse"

              type="checkbox"
              value=""
              class="text-blue-600 bg-gray-100 rounded border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600
                dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
          <label
              for="reverse-checkbox"
              class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
          >
            Reverse
          </label>
        </div>
        <div class="flex items-center">
          <input
              id="iterate-checkbox"
              :class="{
                'checked': state.iterate,
              }"

              v-model="state.iterate"

              type="checkbox"
              value=""
              class="text-blue-600 bg-gray-100 rounded border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600
                dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
          >
          <label for="iterate-checkbox"
                 class="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300">Iterate</label>
        </div>
      </div>
      <div>
        <button
            type="submit"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            @click="addIncludeParam"
        >
          Include
        </button>
      </div>


    </div>
  </div>
</template>


<style scoped>

</style>
