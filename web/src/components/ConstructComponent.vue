<template>
<figure :class="style"
        :draggable="!placeholder"
        @dragstart="ondragstart"
        @dragend="ondragend"
        @dragenter="ondragenter">
  <span class="truncate">{{ infoLine }}</span>
  <div class="flex flex-row">
    <span class="flex-grow transform -translate-y-12">{{ spacers.left }}</span>
    <span class="flex-grow">{{ spacers.right }}</span>
  </div>
</figure>
</template>
<script lang="ts">
import { Vue, Options } from "vue-class-component";
import { PropType } from "vue";

import { PositionType, FragmentInfo } from "../types";

/* TODO(tny): https://github.com/vuejs/vue-class-component/issues/465
 * We would like to use the Vue.with pattern with a TypeScript class to define props, but that sadly
 * does not seem to be possible with vetur + vite + vue3 + other current tooling.
 */
@Options({
    props: {
        info: Object as PropType<FragmentInfo>,
        placeholder: Boolean,
    },
})
export default class ConstructComponent extends Vue {
    // vue-tsc doesn't pick up on props. reassert them in the class itself, even though it's proxied
    // through to the proper props object.
    info!: FragmentInfo;
    placeholder!: boolean;

    beingDragged = false;

    get infoLine() {
        if(this.info.placeholder) return "Drag here ...";
        let posType = Object.keys(PositionType).find(
            // @ts-ignore
            (k) => PositionType[k] == this.info.position.posType
        );
        return `${this.info.name} [${this.info.typ}]`;
    }

    get spacers() {
        if(this.info.placeholder) return {
            left: "",
            right: "",
        };
        return this.info.spacers;
    }

    get style() {
        let common =
            "text-center inline-block w-48 h-16 p-4 m-4 rounded-md border-4 ";
        return (
            common +
                (this.beingDragged || this.info.placeholder
                    ? "border-dashed border-gray-500"
        : "border-solid border-green-400")
    );
    }
    get width() {
        return this.$el.clientWidth;
    }

  ondragstart(e: DragEvent) {
    this.beingDragged = true;
    console.log("dragstart");
    e.dataTransfer!.setData(
      "application/cc-component",
      JSON.stringify(this.info));
    e.dataTransfer!.dropEffect = "copy";
  }

  ondragend() {
    this.beingDragged = false;
  }

    ondragenter(e: DragEvent) {
      e.preventDefault();
  }

    ondragover(e: DragEvent) {
        e.preventDefault();
    }
}
</script>
