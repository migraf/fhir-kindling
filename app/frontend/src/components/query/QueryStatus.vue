<script setup lang="ts">
import {computed, ref, reactive, onMounted} from 'vue'

const props = defineProps({
  status: {type: String, required: true},
  resource: {type: String, required: true},
  query: {type: String, required: true},
  filters: {type: Array, required: false, default: () => []},
  includes: {type: Array, required: false, default: () => []},
  chainParams: {type: Array, required: false, default: () => []},
})

const hl7Url = computed(() => {
  return `https://hl7.org/fhir/${props.resource.toLowerCase()}.html`;
})

const emits = defineEmits(["editResource", "selectTab", "saveQuery", "runQuery"]);

function tabClick(tab: string) {
  console.log("tabClick", tab);
  emits('selectTab', tab);
  state.selectedTab = tab;
}

const state = reactive({
  selectedIndex: 1000,
  searchComplete: false,
  pattern: '',
  selectedTab: 'overview',
})

</script>

<template>
  <div class="flex flex-col bg-gray-800 border-gray-500 shadow-gray-400 shadow-md border rounded-b rounded-t ">
    <div
        class="flex flex-row grow"
    >
      <div
          class="flex flex-col grow"
      >
        <div
            class="flex flex-row flex-grow justify-center mb-2"
        >
          <div class="scrollbar-track-transparent scrollbar flex-row overflow-auto text-gray-200">
            <a
                :href="hl7Url"
                target="_blank"
                class="hover:text-blue-500"
            >
              <div class="inline">
                <span class="text-xl mx-2">
                  <i class="fa-solid fa-circle-info"></i>
                </span>
                <span class="underline text-3xl">
                  {{ props.resource }}
                </span>
              </div>
            </a>
          </div>
          <div class="flex flex-grow items-end justify-end mr-2">
            <div class="flex flex-col justify-items-center text-start mb-1">
              <button
                  class="text-md justify-end hover:text-amber-500 text-orange-300"
                  @click="$emit('editResource')"
              >
                <i class="fa-solid fa-edit"></i>
                Edit
              </button>
            </div>
            <div class="flex flex-col justify-items-center text-start mb-1 ml-4">
              <button
                  class="text-md justify-end hover:text-blue-600 text-blue-300"
                  @click="$emit('saveQuery')"
              >
                <i class="fa-solid fa-save"></i>
                Save
              </button>
            </div>
          </div>
        </div>

        <div
            id="query-status"
            class="flex flex-row flex-grow p-2 items-center"
        >
          <div
              class="text-gray-300 text-xl content-center"
          >
            <i class="fa-solid fa-search"></i>
            Query:
          </div>
          <div
              class="flex flex-grow flex-row justify-items-center
          ml-2 text-gray-200 bg-gray-700 border border-gray-400 rounded-b rounded-t"
          >
            <div class="p-1 pl-2 justify-items-center">
              <span class="text-xl">{{ props.query }}</span>
            </div>
          </div>
          <div class="flex justify-items-center ml-4">
            <button
                class="text-xl justify-end hover:text-green-500 text-green-300"
                @click="$emit('runQuery')"
            >
              <i class="fa-solid fa-play"></i>
              Run
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="flex flex-grow justify-center mt-2">
      <div
          class="text-sm font-medium text-center text-gray-500 border-b border-gray-200 dark:text-gray-400 dark:border-gray-700">
        <ul class="flex flex-wrap -mb-px">
          <li class="mr-2">
            <div
                class="gridinline-block px-4 pb-2 rounded-t-lg border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
                :class="{
                  'border-blue-600 text-blue-600 dark:text-blue-500 dark:border-blue-500': state.selectedTab === 'overview',
                  'active': state.selectedTab === 'overview',
                }"
                @click="tabClick('overview')"
            >
              <div>
                Overview
              </div>
            </div>
          </li>
          <li class="mr-2">
            <div
                class="grid gap-2 grid-cols-3 inline-block px-4 pb-2 rounded-t-lg border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
                :class="{
                  'border-blue-600 text-blue-600 dark:text-blue-500 dark:border-blue-500': state.selectedTab === 'filters',
                  'active': state.selectedTab === 'filters',
                }"
                @click="tabClick('filters')"
            >
              <div
                  class="rounded-full px-1 text-center text-amber-400"
                  :class="{
                    'text-green-600 dark:text-green-600': props.filters.length >= 1,
                  }"
              >
                {{ props.filters.length }}
              </div>
              <div class="col-span-2">
                Filters
              </div>
            </div>
          </li>
          <li class="mr-2">
            <div
                class="grid gap-2 grid-cols-3 inline-block px-4 pb-2 rounded-t-lg border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
                :class="{
                  'border-blue-600 text-blue-600 dark:text-blue-500 dark:border-blue-500': state.selectedTab === 'includes',
                  'active': state.selectedTab === 'includes',
                }"
                @click="tabClick('includes')"
            >
              <div
                  class="rounded-full px-1 text-center text-amber-400"
                  :class="{
                    'text-green-600 dark:text-green-600': props.includes.length >= 1,
                  }"
              >
                {{ props.includes.length }}
              </div>
              <div class="col-span-2">
                Includes
              </div>
            </div>
          </li>
          <li class="mr-2">
            <div
                class="grid gap-2 grid-cols-4 inline-block px-4 pb-2 rounded-t-lg border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
                :class="{
                  'border-blue-600 text-blue-600 dark:text-blue-500 dark:border-blue-500': state.selectedTab === 'chainParams',
                  'active': state.selectedTab === 'chainParams',
                }"
                @click="state.selectedTab = 'chainParams'"
            >
              <div
                  class="rounded-full px-1 text-center text-amber-400"
                  :class="{
                    'text-green-600 dark:text-green-600': props.chainParams.length >= 1,
                  }"
              >
                {{ props.chainParams.length }}
              </div>
              <div class="col-span-3">
                Chain Params
              </div>
            </div>
          </li>
          <li class="mr-2">
            <div
                class="gridinline-block px-4 pb-2 rounded-t-lg border-b-2 border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"
                :class="{
                  'border-blue-600 text-blue-600 dark:text-blue-500 dark:border-blue-500': state.selectedTab === 'results',
                  'active': state.selectedTab === 'results',
                }"
                @click="tabClick('results')"
            >
              <div>
                Results
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>


</template>

<style scoped>

</style>
