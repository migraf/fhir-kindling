<script setup lang="ts">
import {computed, ref, reactive, onMounted} from 'vue'

const props = defineProps({
  status: {type: String, required: true},
  resource: {type: String, required: true},
  query: {type: String, required: true},
})

const hl7Url = computed(() => {
  return `https://hl7.org/fhir/${props.resource.toLowerCase()}.html`;
})

const emits = defineEmits(["editResource"]);

const state = reactive({
  selectedIndex: 1000,
  searchComplete: false,
  pattern: '',
})

</script>

<template>
  <div class="flex flex-col bg-gray-800 border-gray-500 shadow-gray-400 shadow-md border rounded-b rounded-t ">
    <div class="flex flex-row p-2">
      <div
          id="dashboard"
          class="grid grid-cols-6 grow gap-2"
      >
        <div
            class="flex flex-col text-center p-4 justify-between col-span-3"
        >
          <div class="flex text-gray-200 bg-gray-700 justify-items-center border border-gray-400 rounded-b rounded-t">
            <div class="flex p-1 pl-2 justify-items-center">
              <span class="text-xl">{{ props.query }}</span>
            </div>
          </div>
          <div
              class="text-gray-300 text-xl"
          >
            <i class="fa-solid fa-search"></i>
            Query
          </div>
        </div>
        <div
            id="resource-name"
            class="flex-col items-center text-center p-4 justify-between rounded-t rounded-b col-span-2"
        >
          <div class="mb-2 scrollbar-track-transparent scrollbar flex-row overflow-auto text-gray-200">
            <a
                :href="hl7Url"
                target="_blank"
                class="hover:text-blue-500"
            >
              <div class="inline">
              <span class="underline text-2xl">
              {{ props.resource }}
              </span>
                <span class="text-xl ml-1">
                <i class="fa-solid fa-circle-info"></i>
              </span>
              </div>
            </a>
          </div>
          <div class="text-gray-300 text-xl">
            Resource
          </div>
        </div>
        <div class="flex flex-col justify-items-end items-end">
          <button
              class="text-xl justify-end hover:text-amber-500 text-orange-300"
              @click="$emit('editResource')"
          >
            <i class="fa-solid fa-edit"></i>
            Edit
          </button>
        </div>

      </div>
    </div>

    <div class="flex flex-row justify-center">
      <div class="px-2 rounded-t border-gray-500 bg-gray-700 border-l border-t border-r mr-2 shadow-gray-300 shadow shadow-">
        <span class="text-sm font-bold rounded-full mx-1 border border-gray-50 bg-gray-400 text-blue-600 my-0.5 text-center items-center">
          0
        </span>
        Filters
        <button class="hover:text-blue-500">
          <i class="fa-solid fa-angle-down ml-2"></i>
        </button>
      </div>
      <div class="px-2 rounded-t border-gray-500 bg-gray-700 border-l border-t border-r mr-2 shadow-gray-300 shadow">
        <span class="text-sm font-bold rounded-full mx-1 border border-gray-50 bg-gray-400 text-blue-600 py-0 text-center items-center">
          0
        </span>
        Includes
        <button class="hover:text-blue-500">
          <i class="fa-solid fa-angle-down ml-2"></i>
        </button>
      </div>
      <div class="px-2 rounded-t border-gray-500 bg-gray-700 border-l border-t border-r mr-2 shadow-gray-300 shadow">
        <span class="text-sm font-bold rounded-full mx-1 border border-gray-50 bg-gray-400 text-blue-600 my-0.5 text-center items-center">
          0
        </span>
        Chained Params
        <button class="hover:text-blue-500">
          <i class="fa-solid fa-angle-down ml-2"></i>
        </button>
      </div>
    </div>
  </div>


</template>

<style scoped>

</style>
