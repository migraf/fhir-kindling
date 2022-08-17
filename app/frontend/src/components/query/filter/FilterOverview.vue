<script setup lang="ts">
import {computed, ref, reactive, onMounted } from 'vue'
import {FieldParameter} from "../../../domains/query/type";

interface Props {
  filters: Array<FieldParameter>;
  keys?: string[];
  hint?: string;
  button?: boolean;
}

const props = defineProps<Props>()

const state = reactive({
  selectedIndex: 1000,
  searchComplete: false,
  pattern: '',
  displayField: '',
})


</script>


<template>
  <div>

  </div>
</template>



<style scoped>

</style>
