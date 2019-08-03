# Jetpack

Jetpack is an Ansible collection containing useful Ansible add-ons for network engineers and operators.

## Compatibility

Ansible 2.9 required.

## Callback plugins

[`network_change_log`](network_change_log.md): Shows network device changes during a playbook run as well as a per-device summary of changes when the playbook completes.

## Modules

[`cli_parse_transform`](cli_parse_transform.md): An Ansible module that combines the running of commands on a network device with the parsing and transformation of the resulting structured data. Use either `pyats` or the device's `native_json` support for parsing.

[`ready_for_modules`](ready_for_modules): An Ansible module that compares structured data to what an Ansible module expects and removes the extranious information.  It can also be used to split a single dictionary into multiple dictionaries, one for each module desired

### Developer notes, Note to self

As of Aug 1, two WIP changes need to be made for these to work:

```
diff --git a/lib/ansible/executor/task_queue_manager.py b/lib/ansible/executor/task_queue_manager.py
index a4962617a3..6818d3cc56 100644
--- a/lib/ansible/executor/task_queue_manager.py
+++ b/lib/ansible/executor/task_queue_manager.py
@@ -160,6 +160,7 @@ class TaskQueueManager:

         for callback_plugin_name in (c for c in C.DEFAULT_CALLBACK_WHITELIST if is_collection_ref(c)):
             callback_obj = callback_loader.get(callback_plugin_name)
+            callback_obj.set_options()
             self._callback_plugins.append(callback_obj)

         self._callbacks_loaded = True
diff --git a/lib/ansible/template/__init__.py b/lib/ansible/template/__init__.py
index c113075ab7..7627b70216 100644
--- a/lib/ansible/template/__init__.py
+++ b/lib/ansible/template/__init__.py
@@ -350,7 +350,7 @@ class JinjaPluginIntercept(MutableMapping):
                 fq_name = '.'.join((collection_name, f[0]))
                 self._collection_jinja_func_cache[fq_name] = f[1]

-            function_impl = self._collection_jinja_func_cache[key]
+        function_impl = self._collection_jinja_func_cache[key]

         # FIXME: detect/warn on intra-collection function name collisions
```
