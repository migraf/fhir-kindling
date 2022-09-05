<script setup lang="ts">
import {computed, ref, reactive, onMounted, defineEmits} from 'vue'
import {IncludeParameter} from "../../../domains/query/type";
import {urlIncludeParameter} from "../../../domains/query/api";

interface Props {
  includeParams: IncludeParameter[];
}

const props = defineProps<Props>()

const emits = defineEmits(["removeInclude"]);


</script>

<template>
  <div class="flex flex-row border rounded rounded-full rounded-md border-gray-500 p-2 mb-4 mt-2">
    <div
        class="rounded-full rounded-md bg-gray-600 flex items-center justify-center border border-gray-300 mr-2"
        v-for="(parameter, index) in includeParams"
        :key="index"
    >
      <span
          class="pl-2"
      >
        {{
          urlIncludeParameter(parameter)
        }}
      </span>
      <div class="flex items-center justify-between">
        <button
            class="rounded-full rounded-md bg-gray-600 text-white px-2 text-amber-400 hover:text-amber-600"
            @click="$emit('removeInclude', parameter)"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>

</style>
