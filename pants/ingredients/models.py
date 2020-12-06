# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property

from recipes.models import Recipe

from .utils import add_nutrition_ratios

not_negative = MinValueValidator(0)


# TODO utility funcs -> new file
# TODO Include data calcs from recipe etc


class IngredientTag(models.Model):
   """
   Tags for ingredients - just a name.
   Name follows slug rules (only lowercase, hyphens and underscores)
   e.g. grain, meat, legume, pulse, non-perishable
   """
   verbose_name_plural = "Ingredient Tags"

   name = models.SlugField(
      max_length=settings.TAG_LENGTH,
      blank=False,
      unique=True,
   )

   description = models.CharField(max_length=settings.DESCR_LENGTH,blank=True)

   def __str__(self):
      return self.name


class AbstractBaseNutrients(models.Model):
   """
   Abstract Base Class for all Nutrient Set models.
   Common macro values are attributes; micro-stuff like amino acid
   ratios and omega-X fatty acids should be in sub-models.

   Values are per kg - careful when converting from per-100g on packaging.
   Minimum: Calories and Protein; maybe fibre later
   """

   class Meta:
      abstract = True

   # XXX: ALL values are stored per kg (NOT PER 100g!!)
   # TODO: Warn/Remind user of this

   # Was required, but now optional to ease migration to ABC
   # These should still warn if not present TODO
   kilojoules = models.DecimalField(  # NB: there is a prop for calories
      decimal_places=1, # up to 99999.9 kj per kg - pure fat = 37,000 kJ per kg?
      max_digits=6,
      validators=[not_negative],
      blank=True,
      null=True,
   )
   protein = models.DecimalField(
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
      blank=True,
      null=True,
   )

   # These are optional but should still warn if not present TODO
   fibre = models.DecimalField(
      blank=True,
      null=True,
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )
   carbohydrate = models.DecimalField(
      blank=True,
      null=True,
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )

   # Optional but included on packaging so should be present
   fat = models.DecimalField(
      blank=True,
      null=True,
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )
   sugar = models.DecimalField(
      blank=True,
      null=True,
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )
   saturatedfat = models.DecimalField( # TODO validate <= fat
      blank=True,
      null=True,
      decimal_places=3, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )
   sodium = models.DecimalField( # TODO warn careful in mg conversion
      blank=True,
      null=True,
      decimal_places=0, # 1mg precision
      max_digits=6,
      validators=[not_negative],
   )

   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)


class Ingredient(AbstractBaseNutrients):
   """
   A *GENERIC* category of ingredient, like "Rolled Oats"
      - not a specific brand or product
      - not a single foodstuff that can be prepared/sold many ways
        (e.g. Oat Groats, Steel Cut Oats, Quick Oats, Rolled Oats etc
         are different ingredients from the same source)
      - Connected to one set of generic nutrition data; specific
        brands may or may not have a specific set of nutrition data
   """

   class Meta:
        ordering = ["-updated_at"]

   name = models.CharField(
      max_length=settings.NAME_LENGTH,
      blank=False,
      unique=True,
   )
   slug = models.CharField(
      max_length=settings.SLUG_LENGTH,
      blank=True,    # Set automatically; null=False still applies
      unique=True,
   )
   description = models.CharField(max_length=settings.DESCR_LENGTH,blank=True)

   # Owner is null for "global" Ingredients
   # Only owner can see/edit their own ones, only admin can edit global ones
   owner = models.ForeignKey(
      User,
      blank=True,
      null=True,
      on_delete=models.CASCADE,
      related_name='+',       # Prevents User-> related name being created
   )

   tags = models.ManyToManyField(IngredientTag, blank=True)

   serving = models.DecimalField(
      decimal_places=1,
      max_digits=4,     # 999.9g grams per serving
      validators=[not_negative],
      null=True,
      blank=True,
      help_text="Optional grams per serving. WARNING Nutrients are still entered per-KG."
   )

   # These are arbitrary large plain text fields shown on detail page.
   # Page order: Introduction, Nutrition, Notes, Price List
   introduction = models.TextField(blank=True)
   notes = models.TextField(blank=True)

   def __str__(self):
      return self.name

   def save(self, *args, **kwargs):
      if not self.slug:
         self.slug = slugify(self.name)      # NOTE will Exception on clashes
      super(Ingredient, self).save(*args, **kwargs)

   @cached_property
   def sorted_prices(self):
      '''
      Return all the prices of this ingredient, annotated by
      cents_per_kg, and sorted by it.
      '''
      # XXX: If both values are whole numbers, SQLite will silently assume
      # integer division in an F(), possibly discarding a remainder of
      # cents and producing erroneous results. Hence we need to
      # multiply by 100 to ensure the cents are preserved if that
      # happens.

      Price = apps.get_model('products','Price')
      prices = Price.objects.filter(ingredient=self).annotate(
         cents_per_kg = F('price') * 100 / F('weight')
      )
      return prices.order_by('cents_per_kg')

   @cached_property
   def lowest_price(self):
      '''
      Return the Price object which has the lowest price-per-kg of
      this ingredient.
      '''
      return self.sorted_prices.first()

   @cached_property
   def best_price(self):
      """
      Return lowest price per kg from all products of this ingredient,
      as a decimal quantized for display (a value, not a Price object)
      """
      # TODO rename this to "display_lowest_price" or something...
      price = self.lowest_price
      if price:
         return Decimal.quantize(price.per_kg, settings.DECIMAL_CENTS)   # round to cents

   # TODO custom manager for the generic nutrients, use db rather than going
   # through properties! Would also reduce redundancy of these properties
   @cached_property
   def nutrition_data(self):
      """
      Returns all known nutrition data as a dict including ratios (protein/$, fibre/J etc)
      Return should be the same as in recipe and at least contain NUTRITION_DATA_ITEMS
      (Although some may be None)
      """
      data = dict()

      # get required data, generally from nutrient fields but some special cases
      data['cost'] = self.best_price
      data['grams'] = settings.STANDARD_WEIGHT     # data stored per KG or 100g
      if self.serving:
         data['grams_serve'] = self.serving     # optional serving size
      for k in settings.NUTRITION_DATA_ITEMS_BASIC:
         data[k] = getattr(self,k)

      return add_nutrition_ratios(data) # generate ratios and values from above

   # NOTE: This is deprecated, only required for dictsort being flaky
   @cached_property
   def sort_rank(self):
      '''
      Returns the rank from nutrition data, as an integer.
      Returns 0 if there is no rank.
      Used for sorting things that can't sort floating point numbers
      '''
      try:
         return self.nutrition_data['rank']
      except:
         return 0

   @cached_property
   def price_count(self):
      """
      Number of products this ingredient has
      """
      return self.price_set.count()

   # FIXME use the inverse of this approach to optimize the
   # recipe/quantity nutrition_data!
   @cached_property
   def used_in_recipes(self):
      """
      Returns a list dict (slug->name) of Recipes that this
      ingredient is a part of (including child recipes)

      Iterations/queries are proportional to the number of generations
      (not the raw number of recipes).
      """
      Recipe = apps.get_model('recipes','Recipe')
      values = {}
      rqset = Recipe.objects.filter(components__of_ingredient__pk=self.pk)

      while rqset.count():    # until no more child recipes
         values.update(rqset.values_list('slug','name'))   # Add to return list
         rqset = Recipe.objects.filter(components__of_recipe__in=rqset) # Recurse

      return values

class Tag(models.Model):
   """
   Tags for labelling related models across the site. Has name, description, color and icon-name
   e.g. grain, meat, legume, pulse, non-perishable, keto, "New Diet Week 1", etc.
   """

   # The actual tag identifier
   name = models.CharField(
      max_length=settings.TAG_LENGTH,
      blank=False,
      unique=True,
   )

   # An explanation about what this tag is used for
   description = models.CharField(
      max_length=settings.DESCR_LENGTH,
      blank=True
   )

   # An rbg hex code that will be used for this color
   color = models.CharField(
      max_length=8
   )

   # An icon identifier that will be used for this tag
   icon = models.CharField(
      max_length=32
   )

   def __str__(self):
      return self.name

class Taggable(models.Model):
   """
   Abstract model to specify something can be tagged.
   """

   class Meta:
      abstract=True

   tags = models.ManyToManyField(
      Tag,
      related_name="tagged_with"
   )

class Food(AbstractBaseNutrients, Taggable):
   """
   Something that can be eaten, and therefore has nutrition.
   """

   # Human readable name of this food.
   name = models.CharField(
      max_length=settings.NAME_LENGTH,
      blank=False,
      unique=True,
   )
   # A longer description of what this food is.
   description = models.CharField(
      max_length=settings.DESCR_LENGTH,
      blank=True
   )

   # Who has control over this food's information, if null only admin has control
   owner = models.ForeignKey(
      User,
      blank=True,
      null=True,
      on_delete=models.CASCADE,
      related_name='+',  # Prevents User-> related name being created
   )

   # A free form text introduction leading up to this food, useful if taking information from a blog and you want to keep
   # the typical story or history that accompanies the food on food blogs.
   introduction = models.TextField(blank=True)

   # Free form box to keep notes on this food
   notes = models.TextField(blank=True)

class BaseComponent(models.Model):
   """
   Tracks how one food is a component of another food.
   """
   # The parent food that the component belongs to
   recipe = models.ForeignKey(
      'CombinationFood',
      on_delete=models.CASCADE,
      related_name='component_of'
   )

   # The food that is the component of the recipe
   component = models.ForeignKey(
      Food,
      on_delete=models.CASCADE,
      related_name='components'
   )

   # How much of component food (in kg) is being used by the recipe
   amount = models.DecimalField(
      decimal_places=5,  # Down to 0.1 of a gram
      max_digits=9,  # Up to 1000 kgs
      validators=[not_negative],
      help_text="In kilograms",
      null=True,
      blank=True,
   )

   # A note that can be added at the users descretion regarding this component
   note = models.CharField(max_length=settings.DESCR_LENGTH, blank=True)

   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

class CombinationFood(Food):
   """
   Foods which are combinations of other foods in certain ratios, with recipes
   """
   components = models.ManyToManyField(
      Food,
      through=BaseComponent,
      through_fields=('recipe', 'component'),
      related_name='component_set'
   )
   #todo: what if a component is a combinationfood, and the components of that food are just choices, we could add
   # 'choice components'? Or we could change components to give it a type that specifies how to treat the connected food
   # (e.g. oneof, anyof, allof the linked foods components), or we could make combination foods have a type that
   # indicates its a group of choices rather than a real recipe.

class ExtensionFood(CombinationFood):
   """
   Combinations foods which are modifications to other combination foods. The components of this food override the
   components of the parent food if they would otherwise clash
   """
   parent_food = models.ForeignKey(
      CombinationFood,
      on_delete=models.CASCADE,
      related_name='parent_recipe'
   )

   def someFunc(self):
      # Some basic attempt at what a migration would look like for all these new models.
      ingredient = Ingredient()
      food = Food(
         name=ingredient.name,
         description=ingredient.description,
         owner=ingredient.owner,
         introduction=ingredient.introduction,
         notes=ingredient.notes
      )
      recipe = Recipe()
      combination_food = CombinationFood(
         name=recipe.name,
         description=recipe.description,
         owner=recipe.owner,
         introduction=recipe.introduction,
         notes=recipe.notes
      )
      for component in recipe.components:
         base_component = BaseComponent(
            recipe=combination_food,
            component=component.of_recipe__name
         )

