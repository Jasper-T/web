<template>
  <li>
    <div
      class="tree-row"
      :class="{ selected: selectedPath === node.path }"
      :style="{ paddingLeft: `${level * 16 + 8}px` }"
      @click="selectNode"
    >
      <button
        v-if="node.type === 'directory'"
        class="tree-toggle"
        type="button"
        :disabled="node.loading || !node.hasChildren"
        @click.stop="toggleNode"
      >
        <span v-if="node.loading">...</span>
        <span v-else-if="!node.hasChildren">&nbsp;</span>
        <span v-else-if="node.expanded">v</span>
        <span v-else>&gt;</span>
      </button>
      <span v-else class="tree-toggle tree-toggle-placeholder"></span>

      <span class="tree-icon">{{ node.type === "directory" ? "[D]" : "[F]" }}</span>
      <span class="tree-name" :title="node.path">{{ node.name }}</span>
    </div>

    <p v-if="node.error" class="tree-error" :style="{ paddingLeft: `${level * 16 + 32}px` }">
      {{ node.error }}
    </p>

    <ul v-if="node.expanded && node.children?.length" class="tree-list">
      <TreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :level="level + 1"
        :selected-path="selectedPath"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </ul>
  </li>
</template>

<script setup>
defineOptions({ name: "TreeNode" });

const props = defineProps({
  node: {
    type: Object,
    required: true,
  },
  level: {
    type: Number,
    default: 0,
  },
  selectedPath: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["select", "toggle"]);

function selectNode() {
  emit("select", props.node);
}

function toggleNode() {
  emit("toggle", props.node);
}
</script>
