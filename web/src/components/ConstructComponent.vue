<template>
  <figure
    class="w-48 h-16"
    draggable="true"
  >
    <h1>{{ name }} [{{ position.posType }}]</h1>
    <div class="flex flex-row">
      <span class="flex-grow transform -translate-y-12">{{ spacers.left }}</span>
      <span class="flex-grow">{{ spacers.right }}</span>
    </div>
  </figure>
</template>
<script lang="ts">
import { Vue, Options } from 'vue-class-component';
import { PropType } from 'vue';

import { PositionInfo, Spacers } from '../types';
  
@Options({
    props: {
        name: String,
        position: Object as PropType<PositionInfo>,
        spacers: Object as PropType<Spacers>,
    }
})
export default class ConstructComponent extends Vue {
    
}
</script>
