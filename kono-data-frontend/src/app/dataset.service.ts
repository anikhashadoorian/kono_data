import{Injectable}from'@angular/core';

import { Apollo}from 'apollo-angular';
import gql from 'graphql-tag';

const DatasetQuery = gql`
query{
datasets {
id
title
}
}
`;

@Injectable()
export class DatasetService {
constructor(private apollo: Apollo) { }

  all(){
    return this.apollo.watchQuery<any>({ query: DatasetQuery });
  }

}
