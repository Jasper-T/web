<template>
  <main class="app-shell">
    <section class="panel explorer-panel">
      <header class="panel-header">
        <div>
          <p class="eyebrow">Workspace</p>
          <h1>文件浏览器</h1>
        </div>
        <button class="small-button" type="button" @click="reloadRoot">刷新</button>
      </header>

      <div class="tree-container">
        <ul class="tree-list">
          <TreeNode
            :node="rootNode"
            :selected-path="activePath"
            @select="addSelectedPath"
            @toggle="toggleNode"
          />
        </ul>
      </div>
    </section>

    <section class="panel selected-panel">
      <header class="panel-header">
        <div>
          <p class="eyebrow">Selected</p>
          <h2>已选择路径</h2>
        </div>
        <span class="count-badge">{{ selectedPaths.length }}</span>
      </header>

      <label class="select-all">
        <input
          type="checkbox"
          :checked="allSelected"
          :indeterminate="partiallySelected"
          :disabled="selectedPaths.length === 0"
          @change="setAllChecked"
        />
        <span>全选</span>
      </label>

      <div v-if="selectedPaths.length === 0" class="empty-state">
        从左侧点击文件或文件夹后，会显示在这里。
      </div>

      <ul v-else class="selected-list">
        <li v-for="item in selectedPaths" :key="item.path" class="selected-item">
          <label>
            <input v-model="item.checked" type="checkbox" />
            <span :title="item.path">{{ item.path }}</span>
          </label>
        </li>
      </ul>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import TreeNode from "./components/TreeNode.vue";

const workspaceRoot = "/workspace";
const activePath = ref("");
const selectedPaths = ref([]);
const rootNode = ref(createTreeNode({
  name: workspaceRoot,
  path: workspaceRoot,
  type: "directory",
  hasChildren: true,
}));

const allSelected = computed(() => {
  return selectedPaths.value.length > 0 && selectedPaths.value.every((item) => item.checked);
});

const partiallySelected = computed(() => {
  return selectedPaths.value.some((item) => item.checked) && !allSelected.value;
});

function createTreeNode(node) {
  return {
    ...node,
    expanded: false,
    loading: false,
    error: "",
    children: [],
    childrenLoaded: node.childrenLoaded ?? false,
  };
}

async function fetchChildren(path) {
  const response = await fetch(`/api/tree?path=${encodeURIComponent(path)}`);
  if (!response.ok) {
    const fallback = `读取失败：${response.status}`;
    const data = await response.json().catch(() => ({ detail: fallback }));
    throw new Error(data.detail || fallback);
  }
  return response.json();
}

async function loadChildren(node, force = false) {
  if (node.type !== "directory" || node.loading) {
    return;
  }

  if (node.childrenLoaded && !force) {
    return;
  }

  node.loading = true;
  node.error = "";

  try {
    const data = await fetchChildren(node.path);
    node.children = data.children.map(createTreeNode);
    node.childrenLoaded = true;
  } catch (error) {
    node.error = error.message;
  } finally {
    node.loading = false;
  }
}

async function toggleNode(node) {
  if (node.type !== "directory") {
    return;
  }

  node.expanded = !node.expanded;
  if (node.expanded) {
    await loadChildren(node);
  }
}

function addSelectedPath(node) {
  activePath.value = node.path;
  const exists = selectedPaths.value.some((item) => item.path === node.path);
  if (!exists) {
    selectedPaths.value.push({
      path: node.path,
      checked: true,
    });
  }
}

function setAllChecked(event) {
  const checked = event.target.checked;
  selectedPaths.value.forEach((item) => {
    item.checked = checked;
  });
}

async function reloadRoot() {
  rootNode.value.childrenLoaded = false;
  rootNode.value.expanded = true;
  await loadChildren(rootNode.value, true);
}

onMounted(async () => {
  rootNode.value.expanded = true;
  await loadChildren(rootNode.value);
});
</script>
