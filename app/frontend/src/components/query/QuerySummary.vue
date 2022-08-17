<script setup lang="ts">
import {computed, ref, reactive, onMounted } from 'vue'
import {FieldParameter, IncludeParameter} from "../../domains/query/type";

interface Props {
  fieldParams?: FieldParameter[];
  includeParams?: IncludeParameter[];
  chainParams?: FieldParameter[];
}

const props = defineProps<Props>()


</script>

<template>

</template>




<style scoped>

</style>
