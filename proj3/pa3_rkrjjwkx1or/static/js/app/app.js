// /static/js/app/app.js
console.log('entering app.js baby');
window.App = Ember.Application.create();
console.log('just created window.App');

App.Router = Ember.Router.extend({
	rootURL: '/b966cc054de14c43b479/pa3/live'
});

App.Store = DS.Store.extend({});

App.ApplicationAdapter = DS.JSONAPIAdapter.extend({
	namespace: '/b966cc054de14c43b479/pa3/jsonapi/v1'
})

App.Router.map(function() {
	this.route('pic', { path: '/pic/:pic_id' });
});


//pic stuff
App.Pic = DS.Model.extend({
	picurl: DS.attr('string'),
	prevpicid: DS.attr('string'),
	nextpicid: DS.attr('string'),
	caption: DS.attr('string')
});

App.PicRoute = Ember.Route.extend({
	model: function(params) {
		var pic = this.store.findRecord('pic', params.pic_id);
		return pic;
	},

	actions: {
		save: function() {
			var pic = this.modelFor('pic');
			var caption = this.modelFor('pic').get('caption');
			this.set('caption', caption);
			this.modelFor('pic').save();
		}
	},

	renderTemplate: function() {
		this.render('pic');
	}
});