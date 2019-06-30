import{Component}from'@angular/core';
import {Dataset }from './dataset.model';
import {DatasetService}from './dataset.service';

@Component({
selector: 'app-root',
templateUrl: './app.component.html',
styleUrls: ['./app.component.css']
})

export class AppComponent {
title = 'kono-data-frontend';
datasets: Dataset[] = [];

constructor(private datasetService: DatasetService){
      this.datasetService.all().valueChanges.subscribe(
        ({data}) => {
          this.datasets = data.datasets;
        }
      );
  }
}
