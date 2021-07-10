<template>
  <figure class="w-48 h-16">
    <h1>{{ name }}</h1>
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
