<script setup lang="ts">
import {computed, reactive, ref} from "vue";
import {ResourceResults} from "../../../domains/query/type";

interface Props {
  resources: ResourceResults[];
}

const props = defineProps<Props>();

const state = reactive({
  selectedResource: "",
})

const emit = defineEmits(["selectResource"]);

function handleSelectResource(resource: string) {
  emit("selectResource", resource);
  state.selectedResource = resource;
}

</script>

<template>
  <div class="flex flex-col-2 mt-2">
    <div class="h-full">
      <div class="text-gray-100 text-xl">
        Resources:
      </div>
      <div class="flex flex-col flex-grow border border-gray-500 rounded px-2 pb-2 h-full">
        <div
            v-for="resource in resources"
            :key="resource.resource"
            class="flex flex-row p-2 border rounded border-gray-500 shadow shadow-sm shadow-gray-400
            hover:shadow-lg hover:shadow-gray-500 hover:bg-gray-800 mt-2"
            @click="handleSelectResource(resource.resource)"
            :class="{'bg-gray-800 border-blue-500': state.selectedResource === resource.resource}"
        >
          <div class="flex flex-row">
            <div class="text-gray-100 text-md">
              {{ resource.resource }}
            </div>
            <div class="text-gray-100 text-md pl-2">
              ({{ resource.items.length }})
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>


<style scoped>

</style>
