import{BrowserModule}from'@angular/platform-browser';
import {NgModule }from '@angular/core';

import {ApolloModule, APOLLO_OPTIONS}from 'apollo-angular';
import {ApolloClient}from 'apollo-client';
import {HttpLinkModule, HttpLink}from "apollo-angular-link-http";
import {InMemoryCache}from "apollo-cache-inmemory";

import {AppRoutingModule} from './app-routing.module';
import {AppComponent}from './app.component';

import {DatasetService}from './dataset.service';

@NgModule({
declarations: [
AppComponent
],
imports: [
BrowserModule,
AppRoutingModule,
ApolloModule
],
providers: [{
provide: APOLLO_OPTIONS,
useFactory: (httpLink: HttpLink) => {
      return {
        cache: new InMemoryCache(),
        link: httpLink.create({
          uri: 'http://127.0.0.1:8000/graphql'
        })
      }
    },
    deps: [HttpLink]
  },
    DatasetService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
