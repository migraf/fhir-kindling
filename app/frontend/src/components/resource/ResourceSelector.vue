<script setup lang="ts">
import {computed, ref} from 'vue'
import Fuse from "fuse.js";

const props = defineProps({
  resourceNames: {type: Array, required: true},
})

const options = {
  includeScore: true
}

const pattern = ref('');

const fuse = new Fuse(props.resourceNames, options);

const matches = computed(() => {
  return fuse.search(pattern.value)
})

const loading = ref(false);


</script>

<template>
  <form class="flex items-center">
    <label for="simple-search" class="sr-only">Search</label>
    <div class="relative w-full">
      <div class="flex absolute inset-y-0 left-0 items-center pl-3 pointer-events-none">
        <svg aria-hidden="true" class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20"
             xmlns="http://www.w3.org/2000/svg">
          <path fill-rule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clip-rule="evenodd"></path>
        </svg>
      </div>
      <input v-model="pattern" type="text" id="simple-search"
             class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
             placeholder="Enter resource" required>
      <div
          v-if="matches.length > 0"
          class="absolute overflow-scroll top-100 mt-1 w-full border bg-gray-50 dark:bg-gray-700 shadow-xl rounded max-h-64 scrollbar scrollbar-thumb-gray-900 scrollbar-track-transparent divide-gray-500 divide-y"
      >
        <div
            class="p-3 text-gray-900 dark:text-white"
            v-for="match in matches"
        >
          {{match.item}}
        </div>

      </div>
    </div>
    <button type="submit"
            class="p-2.5 ml-2 text-sm font-medium text-white bg-blue-700 rounded-lg border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
      </svg>
      <span class="sr-only">Search</span>
    </button>
  </form>

</template>

<style scoped>
.scrollbar::-webkit-scrollbar {
  width: 20px;
  height: 20px;
}

.scrollbar::-webkit-scrollbar-track {
  border-radius: 100vh;
  background: #f7f4ed;
}

.scrollbar::-webkit-scrollbar-thumb {
  background: #e0cbcb;
  border-radius: 100vh;
  border: 3px solid #f6f7ed;
}

.scrollbar::-webkit-scrollbar-thumb:hover {
  background: #c0a0b9;
}

</style>
