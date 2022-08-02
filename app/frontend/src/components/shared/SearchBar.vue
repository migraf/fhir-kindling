<script setup lang="ts">
import {computed, ref, reactive, onMounted} from 'vue'
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
  return fuse.search(state.pattern)
})

const loading = ref(false);
const state = reactive({
  selectedIndex: 1000,
  searchComplete: false,
  pattern: '',
})

const itemRefs = ref([])
const list = ref([
  /* ... */
])

function arrowDownPress() {
  console.log("arrowDownPress");
  if (state.selectedIndex === 1000) {
    state.selectedIndex = 0;
    console.log("first")
  } else {
    if (state.selectedIndex < matches.value.length - 1) {
      state.selectedIndex++;
      const el = itemRefs.value[state.selectedIndex];
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    }
  }
  console.log(state.selectedIndex);
  console.log(itemRefs.value)
}

function arrowUpPress() {
  console.log("arrowUpPress");
  if (state.selectedIndex === 1000) {
    state.selectedIndex = 1000;
  } else {
    if (state.selectedIndex === 0) {
      state.selectedIndex = 1000;
    } else {
      state.selectedIndex--;
    }
  }
  console.log(state.selectedIndex);
}

const emit = defineEmits(['selected', 'submit'])

function handleSelect(index: number) {
  console.log("handleSelect", index);
  state.selectedIndex = index;
  state.searchComplete = true;
  state.pattern = "";
  emit("selected", props.resourceNames[index]);

}

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
      <input v-model="state.pattern" type="text" id="simple-search"
             class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
             @keyup.down.prevent="arrowDownPress"
             @keyup.up.prevent="arrowUpPress"
             @focus="state.searchComplete = false"
             placeholder="Enter resource" required>
      <div
          v-if="matches.length > 0 && !state.searchComplete"
          class="absolute overflow-scroll top-100 mt-1 w-full border bg-gray-50 dark:bg-gray-700 shadow-xl rounded max-h-64 scrollbar scrollbar-thumb-gray-900 scrollbar-track-transparent divide-gray-500 divide-y"
          @keyup.down.prevent="arrowDownPress"
          @keyup.up.prevent="arrowUpPress"
          @keyup.enter="handleSelect(state.selectedIndex)"
      >
        <div
            class="p-3 text-gray-900 dark:text-white"
            v-for="(match, index) in matches"
            :key="match.item"
            @keyup.enter="handleSelect(match.refIndex)"
            @click="handleSelect(match.refIndex)"
        >
          <div
            :class="{'bg-blue-500 dark:bg-blue-700': state.selectedIndex === index}"
            ref="itemRefs"
          >
            {{ match.item }}
          </div>
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

</style>
