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

</script>

<template>
  <div class="flex flex-row border rounded-b rounded-t p-2 bg-gray-700 border-gray-500">
    <div
        id="dashboard"
        class="grid grid-cols-6 grow gap-2"
    >
      <div
          id="resource-name"
          class="flex-col items-center text-center p-4 justify-between rounded-t rounded-b col-span-2"
      >
        <div class="mb-2 scrollbar-track-transparent scrollbar flex-row overflow-auto">
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
      <div
          class="flex flex-col text-center p-4 justify-between col-span-3"
      >
        <div class="flex text-gray-100 bg-gray-600 justify-items-center border border-gray-400 rounded-b rounded-t">
          <div class="flex pl-1 pr-1 justify-items-center">
            <span class="text-xl">{{ props.query }}</span>
          </div>
        </div>
        <div
            class="text-gray-300 text-xl"
        >
          Query
        </div>
      </div>
      <div class="flex flex-col justify-items-end items-end">
        <button
            class="text-xl justify-end hover:text-amber-500"
            @click="$emit('editResource')"
        >
          <i class="fa-solid fa-edit"></i>
          Edit
        </button>
      </div>

    </div>
  </div>

</template>

<style scoped>

</style>
