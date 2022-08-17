<script setup lang="ts">
import {reactive, ref} from "vue";
import {ResourceField} from "../../domains/resource/type";
import SearchBar from "../common/SearchBar.vue";

interface Props {
  resource: string;
  fields: ResourceField[];
}

const props = defineProps<Props>()

const state = reactive({
  selectedField: '',
  filters: {
    extensions: true,
    default: true,
  }
})

function handleFieldSelect(item: string) {
  console.log("handleFieldSelect", item);
  state.selectedField = item;
}


</script>

<template>
  <div class="flex grid gap-4 grid-cols-5 flex-grow">
    <div class="col-span-2">
      <SearchBar
          v-if="state.selectedField === ''"
          :items="fields"
          @selected="handleFieldSelect"
          :hint="'Select a field...'"
          :keys="['name', 'description', 'title']"
      >
      </SearchBar>
    </div>
    <div class="">
      operator
    </div>
    <div class="col-span-2">
      value
    </div>
  </div>
</template>

<style scoped>

</style>
