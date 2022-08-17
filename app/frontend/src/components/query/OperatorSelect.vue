<script setup lang="ts">
import {reactive, ref} from "vue";
import {Operators} from "../../domains/query/type";


const options = ref(
    Object.keys(Operators).map((key, index) => {
        return {
            label: Object.values(Operators)[index],
            value: key,
        };
    }),
);
const selected = ref('');

const emits = defineEmits(["operatorSelected"]);
function handleOperatorSelect() {
    console.log("handleOperatorSelect", selected.value);
    emits("operatorSelected", selected.value);
}

</script>

<template>
  <select
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500
            focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
            dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      @change="handleOperatorSelect"
      v-model="selected"
  >
    <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
    >
      {{ option.label }}
    </option>
  </select>
</template>



<style scoped>

</style>
