import { Component } from '@angular/core';
import { JobServiceService } from '../job-service.service';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrl: './job-list.component.scss'
})
export class JobListComponent {

  constructor(private jobService:JobServiceService){
    this.getHello()

  }

  getHello(){
    this.jobService.getHello().subscribe({
      next:(res=>{
        console.log(res)
      }),
      error:(err=>{
        console.log(err)
      })
    })
  }

}
