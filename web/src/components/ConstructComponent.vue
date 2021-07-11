<template>
  <figure
    class="w-48 h-16 p-4 m-4 rounded-md border-solid border-4 border-green-400"
    draggable="true"
  >
    <span class="truncate">{{ name }} [{{ posTypeName }}]</span>
    <div class="flex flex-row">
      <span class="flex-grow transform -translate-y-12">{{ spacers.left }}</span>
      <span class="flex-grow">{{ spacers.right }}</span>
    </div>
  </figure>
</template>
<script lang="ts">
import { Vue, Options } from 'vue-class-component';
import { PropType } from 'vue';

import { PositionInfo, PositionType, Spacers } from '../types';

  
@Options({
    props: {
        name: String,
        position: Object as PropType<PositionInfo>,
        spacers: Object as PropType<Spacers>,
    }
})
export default class ConstructComponent extends Vue {
    get posTypeName() {
        // @ts-ignore
        return Object.keys(PositionType).find(k => PositionType[k] == this.position.posType);
    }
}
</script>
