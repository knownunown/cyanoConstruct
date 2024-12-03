<template>
  <main class="grid grid-rows-3 grid-flow-col-dense md:grid-cols-4 h-screen max-h-screen">
    <section
      id="component-selection"
      class="md:row-span-2 md:col-span-3 overflow-y-auto"
    >
      <construct-component
        v-for="item in sample"
        :key="item.position.pos + '_' + item.name"
        :info="item"
      />
    </section>
    <section
      id="construct"
      class="md:row-span-1 md:col-span-4 overflow-x-auto p-2"
    >
      <construct-builder />
    </section>
    <section
      id="construct-meta"
      class="md:row-span-2 md:col-span-1 p-2"
    >
      <span>Info</span>
      <div>
        <input
          type="radio"
          name="backboneType"
          value="integrative"
        >
        <label for="integrative">Integrative</label>
        <br>
        <input
          type="radio"
          name="backboneType"
          value="replicative"
        >
        <label for="replicative">Replicative</label>
      </div>
    </section>
  </main>
</template>

<script lang="ts">
import { Vue, Options } from 'vue-class-component';

import ConstructComponent from './components/ConstructComponent.vue'
import ConstructBuilder from './components/ConstructBuilder.vue'
import { FragmentInfo } from './types';

import sampleData from '../data.json';

@Options({
    components: { ConstructComponent, ConstructBuilder }
})

export default class App extends Vue {
    get sample(): Array<FragmentInfo> {
        console.log(sampleData);
        /*
        return {[{
              pos: {
              posType: PositionType.Middle,
              pos: 1
              },
              spacers: {
              left: "AAAA",
              right: "CAGA"
              }
              }]
            data: sampleData as Array<Data>
        };*/
        return sampleData as Array<FragmentInfo>;
    }
}
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
}
</style>
