<template>
  <construct-component
    v-for="item in data"
    :name="'foo'"
    :position="item.pos"
    :spacers="item.spacers"
  />
  <p class="transform rotate-45">Wacky and wild!</p>
</template>
<script lang="ts">
import { Vue, Options } from 'vue-class-component';

import ConstructComponent from './components/ConstructComponent.vue'
import { PositionInfo, PositionType, Spacers } from './types';

interface Data {
    pos: PositionInfo,
    spacers: Spacers,
}

@Options({
    components: { ConstructComponent }
})
export default class App extends Vue {
    data() {
        return {
            data: [{
                pos: {
                    posType: PositionType.Middle,
                    pos: 1
                },
                spacers: {
                    left: "AAAA",
                    right: "CAGA"
                }
            }] as Array<Data>
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
