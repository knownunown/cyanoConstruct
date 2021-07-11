<template>
  <div class="flex flex-row overflow-x-auto">
  <construct-component
    v-for="item in data"
    :name="item.name"
    :position="item.pos"
    :spacers="item.spacers"
  />
  </div>
</template>

<script lang="ts">
import { Vue, Options } from 'vue-class-component';

import ConstructComponent from './components/ConstructComponent.vue'
import { PositionInfo, PositionType, Spacers } from './types';

import sampleData from '../data.json';

interface Data {
    name: String,
    pos: PositionInfo,
    spacers: Spacers,
}

@Options({
    components: { ConstructComponent }
})

export default class App extends Vue {
    data() {
        console.log(sampleData);
        return {
            data: /*[{
                pos: {
                    posType: PositionType.Middle,
                    pos: 1
                },
                spacers: {
                    left: "AAAA",
                    right: "CAGA"
                }
            }]*/
            sampleData as Array<Data>
        };
    }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
