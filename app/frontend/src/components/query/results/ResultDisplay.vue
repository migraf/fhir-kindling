<script setup lang="ts">
import {reactive, ref} from "vue";
import {ResourceResults} from "../../../domains/query/type";
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';

interface Props {
  result: ResourceResults;
}

const props = defineProps<Props>()

</script>

<template>
  <div class="flex flex-grow overflow-y-scroll border border-gray-500 p-2 rounded mt-4
  scrollbar-thumb-gray-900 scrollbar-track-gray-500">
    <vue-json-pretty
        :data="props.result.items"
        class="result-display"
    >

    </vue-json-pretty>
  </div>
</template>



<style scoped>

.result-display {
  width: 100%;
  height: 60vh;
}

</style>
