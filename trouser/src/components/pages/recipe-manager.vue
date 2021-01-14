<template>
    <div id="recipe-manager">
        <div class="header-all-recipes flex-row-between flex-gap-regular">
            <h2>Food</h2>
            <input-float
                    id='recipe_filter'
                    label='Search'
                    v-model="searchTerm"
            />
        </div>
        <div class="all-recipes resizable-vertical">
            <ag-grid-vue
                    id="recipes-table"
                    class="ag-theme-balham"
                    :gridOptions="recipeGrid.gridOptions"
                    :frameworkComponents="recipeGrid.frameworkComponents"
                    :columnDefs="recipeGrid.columnDefs"
                    :defaultColDef="recipeGrid.defaultColDef"
                    :rowModelType="recipeGrid.rowModelType"
                    :rowSelection="recipeGrid.rowSelection"
                    :pagination="recipeGrid.pagination"
                    :paginationAutoPageSize="recipeGrid.paginationAutoPageSize"
                    :datasource="recipeGrid.datasource"
                    @row-selected="onRecipeRowSelected"
            />
        </div>
        <div class="all-ingredients resizable-vertical">
            <ag-grid-vue
                    id="ingredients-table"
                    class="ag-theme-balham"
                    :gridOptions="componentsGrid.gridOptions"
                    :frameworkComponents="componentsGrid.frameworkComponents"
                    :columnDefs="componentsGrid.columnDefs"
                    :defaultColDef="componentsGrid.defaultColDef"
                    :rowModelType="componentsGrid.rowModelType"
                    :pagination="componentsGrid.pagination"
                    :paginationAutoPageSize="componentsGrid.paginationAutoPageSize"
                    :datasource="componentsGrid.datasource"
            />
        </div>
        <div class="recipe">
            <form id="recipe-edit-form" autocomplete="off">
                <input type="hidden" id="selected_row_node" />
                <input type="hidden" id="recipe_uri" name="recipe_uri" />

                <input-float
                        id='introduction'
                        label='Introduction'
                        hint="Some food bloggers life story..."
                        :multiline="true"
                        v-model="recipe.introduction"
                        v-show="showAllFields"
                />

                <div class="flex-row-equalfill">
                    <input-float
                            id='name'
                            label='Name'
                            hint="Grilled Cheese"
                            v-model="recipe.name"
                    />
                    <input-float
                            id='slug'
                            label='Slug'
                            hint="grilled-cheese"
                            input_mask_name="slug_mask"
                            v-model="recipe.slug"
                            v-show="showAllFields"
                    />
                </div>

                <input-float
                        id='description'
                        label='Description'
                        hint="A sandwich made with melted cheese"
                        :multiline="true"
                        v-model="recipe.description"
                />

                <div class="flex-row-equalfill" style="align-items: baseline">
                    <input-float
                            id='serves'
                            label='Serves'
                            hint="1"
                            v-model="recipe.serves"
                    />
                    <input-float
                            id='tags'
                            label='Tags'
                            hint="tag1,tag2,tag3"
                            input_mask=tag_mask
                            :extra='{style:"flex:2"}'
                            v-model="recipe.tags"
                            v-show="showAllFields"
                    />
                    <!-- @todo it is unclear what flag is used for, need to add support for it -->
                    <input-float
                            id="flag"
                            type="select"
                            label="Flag"
                            v-model="recipe.flag"
                            v-show="showAllFields"
                    >
                        <option v-for="flag in allowedFlags" :key="flag.name" :value="flag.name">({{flag.char}})
                            {{flag.name}}
                        </option>
                    </input-float>
                </div>

<!--                <h3>Ingredients</h3>-->
                <div
                        id="recipe-components"
                        v-if="recipe.components.length"
                >
                    <recipe-component
                            v-for="(component, idx) in recipe.components" :key="component.id"
                            :id="component.id"
                            :name="component.name"
                            :recipe_or_ingredient_id="component.recipe_or_ingredient_id"
                            :type="component.type"
                            :note.sync="component.note"
                            :unit.sync="component.unit"
                            :amount.sync="component.amount"
                            :include-labels="false"
                            @delete="recipe.components.splice(idx, 1)"
                    />
                </div>
                <p v-else class="no-components-warning">Recipe has no ingredients</p>

                <input-float
                        id='method'
                        label='Method'
                        hint="Add cheese to bread, toast."
                        :multiline="true"
                        v-model="recipe.method"
                />
                <input-float
                        id='notes'
                        label='Notes'
                        hint="Can use different cheeses than what is listed. Recipe is flexible."
                        :multiline="true"
                        v-model="recipe.notes"
                        v-show="showAllFields"
                />
            </form>
            <div class="form-actions">
                <input-checkbox
                        id="showMore"
                        v-model="showAllFields"
                        label="Advanced"
                />
                <site-button
                        :disabled="!canDelete"
                        v-show="canDelete && showAllFields"
                        @click.native="delete_recipe"
                >
                    Delete
                </site-button>
                <site-button
                        :primary="!canEdit"
                        @click.native="create_recipe"
                >
                    Save {{recipe.uri ? "Copy" : "New"}}
                </site-button>
                <site-button
                        :primary="canEdit"
                        :disabled="!canEdit"
                        v-show="canEdit"
                        @click.native="edit_recipe"
                >
                    Save
                </site-button>
            </div>
        </div>
    </div>
</template>

<script>
    import InputFloat from "@/components/inputs/input-float";
    import {AgGridVue} from 'ag-grid-vue';
    import RecipeComponent from "@/components/recipe-component";

    import "ag-grid-community/dist/styles/ag-grid.css";
    import "ag-grid-community/dist/styles/ag-theme-balham.css";

    import ActionButtonCellRenderer from '@/components/cell-renderers/action-button';
    import SiteButton from "@/components/inputs/site-button";
    import InputCheckbox from "@/components/inputs/input-checkbox";

    export default {
        name: "recipe-manager",
        components: {
            InputCheckbox,
            SiteButton,
            RecipeComponent,
            InputFloat,
            AgGridVue
        },
        inject: ['pants'],
        data() {
            return {
                recipeGrid: {
                    gridOptions: {},
                    frameworkComponents: {
                        actionsCell: ActionButtonCellRenderer,
                    },
                    columnDefs: [
                        {
                            headerName: "", // "Actions" doesn't fit and gets awkwardly cut off
                            cellRenderer: "actionsCell",
                            cellRendererParams: {
                                onClick: recipe => {
                                    this.add_component(
                                        "recipe",
                                        undefined, // There is no database id since this is a newly added component
                                        recipe.url.split("/").slice(-2)[0],
                                        recipe.name,
                                        "",
                                        "servings");
                                },
                                icon: "hamburger"
                            },
                            cellStyle: {"padding": "0"},
                            maxWidth: 25,
                            pinned: "left",
                        },
                        {headerName: "Recipe", field: "name", pinned: "left", width: 125},
                        {headerName: "Description", field: "description"},
                        {headerName: "Serves", field: "serves", maxWidth: 65}, // Just the size of the header and no more
                        {headerName: "Notes", field: "notes"},
                    ],
                    defaultColDef: {
                        flex: 1,
                        sortable: true,
                        resizable: true,
                        minWidth: 100,
                    },
                    rowModelType: 'infinite',
                    rowSelection: 'single',
                    pagination: true,
                    paginationAutoPageSize: true,
                    // Set up the grid to paginate using the server side API
                    datasource: {
                        getRows: async params => {
                            params.searchKey = this.searchTerm;
                            let response = await this.pants.get_recipes(params);

                            if (response.ok) {
                                let data = await response.json();
                                params.successCallback(data['results'], data['count'])
                            } else {
                                params.failCallback();
                            }
                        }
                    }
                },
                componentsGrid: {
                    gridOptions: {},
                    frameworkComponents: {
                        actionsCell: ActionButtonCellRenderer,
                    },
                    columnDefs: [
                        {
                            headerName: "", //"Actions" doesn't fit and gets awkwardly cut off
                            cellRenderer: "actionsCell",
                            cellRendererParams: {
                                onClick: ingredient => {
                                    this.add_component(
                                        "ingredient",
                                        undefined, // There is no database id since this is a newly added component
                                        ingredient.url.split("/").slice(-2)[0],
                                        ingredient.name,
                                        "",
                                        "weight");
                                },
                                icon: "carrot"
                            },
                            cellStyle: {"padding": "0"},
                            maxWidth: 25,
                            pinned: "left",
                        },
                        {headerName: "Ingredient", field: "name", pinned: "left", width: 125},
                        {headerName: "Description", field: "description"},
                        {headerName: "Serving", field: "serving", maxWidth: 65},
                        {headerName: "Notes", field: "notes"},
                    ],
                    defaultColDef: {
                        flex: 1,
                        sortable: true,
                        resizable: true,
                        minWidth: 100,
                    },
                    rowModelType: 'infinite',
                    pagination: true,
                    paginationAutoPageSize: true,
                    // Set up the grid to paginate using the server side API
                    datasource: {
                        getRows: async params => {
                            params.searchKey = this.searchTerm;
                            let response = await this.pants.get_ingredients(params);

                            if (response.ok) {
                                let data = await response.json();
                                params.successCallback(data.results, data.count)
                            } else {
                                params.failCallback();
                            }
                        }
                    }
                },
                recipe: {
                    components: [],
                    uri: null,
                    introduction: null,
                    name: null,
                    slug: null,
                    description: null,
                    serves: null,
                    tags: null,
                    flag: null,
                    method: null,
                    notes: null,
                },
                focusedNode: null,
                allowedFlags: [],
                // If all form fields should show. Hide the most uncommon fields by default.
                showAllFields: false,
                // What term will be used to search for recipes and ingredients
                searchTerm: "",
            }
        },
        watch:{
            searchTerm(){
                this.refreshTables();
            }
        },
        computed: {
            canEdit() {
                return this.focusedNode != null;
            },
            canDelete() {
                return this.focusedNode != null;
            }
        },
        mounted() {
            // Set flag options
            this.pants.get_recipe_flags()
                .then(data => {
                    this.allowedFlags = data.results;
                });
        },
        methods: {
            /**
             * Gets all the components in the components list and returns a list suitable for passing onto the api
             */
            get_components() {
                let output = [];
                this.recipe.components.forEach(component => {
                    let component_obj = {
                        name: component.name,
                        note: component.note || '',
                        // Set "servings" or "weight"
                        [component.unit]: component.amount,
                        // Set "of_ingredient" or "of_recipe"
                        ["of_" + component.type]: component.recipe_or_ingredient_id,
                    }
                    if (component.id) {
                        // Only set db id if it has been provided by the db
                        component_obj["id"] = component.id;
                    }
                    output.push(component_obj)
                })
                return output;
            },
            /**
             * Adds a component to the component list
             * @param {string} type either "recipe" or "ingredient"
             * @param {number} id the id number of the component (not the url) for this component relationship
             * @param {number|string} recipe_or_ingredient_id the original recipe or ingredient id for this component
             * @param {string} name the name of the component
             * @param {number|string} amount how much of the component in units
             * @param {string} unit what unit the amount is in. Should be "weight" for grams, or "servings" for servings
             * @param {string} note any additional notes
             */
            add_component(type, id, recipe_or_ingredient_id, name, amount, unit, note) {
                this.recipe.components.push({
                    type: type,
                    id: id,
                    recipe_or_ingredient_id: parseFloat(recipe_or_ingredient_id),
                    name: name,
                    amount: parseFloat(amount) || 0,
                    unit: unit,
                    note: note
                });
            },
            /**
             * Deletes the currently selected recipe
             */
            delete_recipe() {
                this.pants.delete_recipe(this.recipe.uri)
                    .then(() => {
                        this.recipeGrid.gridOptions.api.deselectAll();
                        this.recipeGrid.gridOptions.api.refreshInfiniteCache();
                        // Clear form
                        for (let key of Object.keys(this.recipe)) {
                            this.recipe[key] = null
                        }
                    });
            },
            /**
             * Updates the recipe based on the values in the recipe form
             */
            edit_recipe() {
                this.pants.edit_recipe(this.recipe.uri, {
                    name: this.recipe.name,
                    slug: this.recipe.slug,
                    description: this.recipe.description,
                    // @todo Cannot edit owner? Remove this if there is no case where this is possible
                    // 'owner': form.querySelector('[name=owner]').value,
                    tags: this.recipe.tags.split(',').filter(tag => tag !== ''), // Remove empty tags
                    serves: this.recipe.serves,
                    introduction: this.recipe.introduction,
                    notes: this.recipe.notes,
                    method: this.recipe.method,
                    components: this.get_components(),
                    flag: this.recipe.flag,
                })
                    .then(resp => {
                        let row_node = this.focusedNode;
                        row_node.setData(resp);
                        this.recipeGrid.gridOptions.api.flashCells({
                            rowNodes: [row_node]
                        })
                    });
            },
            /**
             * Creates a new recipe using the information in the recipe form
             */
            create_recipe() {
                this.pants.create_recipe({
                    name: this.recipe.name,
                    slug: this.recipe.slug,
                    description: this.recipe.description,
                    // @todo Cannot edit owner? Remove this if there is no case where this is possible
                    // 'owner': form.querySelector('[name=owner]').value,
                    tags: this.recipe.tags.split(',').filter(tag => tag !== ''), // Remove empty tags,
                    serves: this.recipe.serves,
                    introduction: this.recipe.introduction,
                    notes: this.recipe.notes,
                    method: this.recipe.method,
                    components: this.get_components(),
                    flag: this.recipe.flag,
                })
                    .then(() => {
                        this.recipeGrid.gridOptions.api.refreshInfiniteCache();
                    });
            },
            remove_all_components() {
                this.recipe.components = [];
            },
            onRecipeRowSelected(args) {
                // This event fires if a row is selected OR deselected, we only care if something gets selected
                if (!args.node.selected) return;
                let recipe = args.data;

                this.recipe.introduction = recipe.introduction;
                this.recipe.name = recipe.name;
                this.recipe.description = recipe.description;
                this.recipe.uri = recipe.url;
                this.recipe.serves = recipe.serves;
                this.recipe.flag = recipe.flag || "";
                this.recipe.method = recipe.method;
                this.recipe.notes = recipe.notes;
                this.recipe.tags = recipe.tags.join(',');
                this.recipe.slug = recipe.slug;

                // Components are not included in results for performance reasons, make a separate call to get those
                this.pants.get_recipe_full(recipe.url)
                    .then(response => response.json())
                    .then(json => {
                        // Empty current components
                        this.remove_all_components();

                        json.components.forEach(component => {
                            this.add_component(
                                component.of_ingredient == null ? "recipe" : "ingredient",
                                component.id,
                                component.of_ingredient || component.of_recipe,
                                component.name,
                                component.servings || component.weight,
                                component.servings == null ? "weight" : "servings",
                                component.note
                            );
                        })
                    })
                    .catch(e => {
                        console.log(e);
                        // Don't leave components from last recipe in there.
                        this.remove_all_components();
                    })

                // Also store a reference to this node so that we can refresh it
                this.focusedNode = args.node;
            },
            refreshTables(){
                // For some reason, refreshInfiniteCache only works if some blocks are already loaded
                // If no results exist in the table (say because they all got filtered), then refreshInfiniteCache won't
                // work as there are no blocks to mark dirty. In that case we purge instead
                // @todo extract this to some utility function
                if(Object.keys(this.recipeGrid.gridOptions.api.getCacheBlockState()).length){
                    this.recipeGrid.gridOptions.api.refreshInfiniteCache();
                }
                else {
                    this.recipeGrid.gridOptions.api.purgeInfiniteCache();
                }
                if(Object.keys(this.componentsGrid.gridOptions.api.getCacheBlockState()).length){
                    this.componentsGrid.gridOptions.api.refreshInfiniteCache();
                }
                else {
                    this.componentsGrid.gridOptions.api.purgeInfiniteCache();
                }
            },
        }
    }
</script>

<style scoped lang="scss">
    @import 'src/assets/css/responsive';
    @mixin resizeable-vertical {
        resize: vertical;
        overflow: auto;
    }

    #recipe-manager {
        display: grid;
        grid:
                "header-all-recipes" max-content
                "all-recipes" 10em
                "header-all-ingredients" max-content
                "all-ingredients" 10em
                "header-recipe" max-content
                "recipe" 1fr
        / 1fr;
        gap: var(--padding) 0;

        min-height: 100%; /* Make it fill the screen as much as possible for less flash when picking a recipe*/

        > .header-all-recipes {
            grid-area: header-all-recipes;
        }

        > .all-recipes {
            grid-area: all-recipes;
            @include resizeable-vertical;

            #recipes-table {
                height: 100%;
            }
        }

        > .header-all-ingredients {
            grid-area: header-all-ingredients;
        }

        > .all-ingredients {
            grid-area: all-ingredients;
            @include resizeable-vertical;

            #ingredients-table {
                height: 100%;
            }
        }

        > .header-recipe {
            grid-area: header-recipe;
        }

        > .recipe {
            grid-area: recipe;

            #recipe-components {
                display: grid;
                grid-template-columns: [note-start] 1em 1fr [note-end] 5em 6em;
                margin: var(--padding) 0 var(--padding) var(--padding);
                align-items: baseline;

                ::v-deep .recipe-component {
                    .name{
                        padding-left: 1em;
                    }
                    .note {
                        grid-column: note-start / note-end
                    }
                }
            }

            .no-components-warning{
                color: grey;
                font-size: 0.8em;
                padding: 1em;
            }
            .form-actions{
                display: flex;
                justify-content: flex-end;
            }
        }

        ::v-deep {
            .field, button {
                margin: 1px;
            }
        }
    }

    @include breakpoint-from(md){
        #recipe-manager{
            grid:
                    "header-all-recipes header-recipe" max-content
                    "all-recipes recipe" 1fr
                    "header-all-ingredients recipe" max-content
                    "all-ingredients recipe" 1fr
                    / 1fr 30em;
            gap: 0 var(--padding);
        }
    }
</style>