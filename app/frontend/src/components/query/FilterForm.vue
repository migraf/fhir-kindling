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
  },
  searchKeys: ["name", "title", "description"],
})

function handleFieldSelect(item: string) {
  console.log("handleFieldSelect", item);
  state.selectedField = item;
}


</script>

<template>
  <div class="flex grid gap-4 grid-cols-5 flex-grow p-2">
    <div class="col-span-2">
      <SearchBar
          :items="fields"
          @selected="handleFieldSelect"
          :hint="'Select a field...'"
          :keys="state.searchKeys"
      >
        <template v-slot="slotProps">
          <div>
            {{ slotProps.content.name }}
          </div>
        </template>
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
