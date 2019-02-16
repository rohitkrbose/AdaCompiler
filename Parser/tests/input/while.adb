with Ada.Text_IO, Ada.Integer_Text_IO;
use Ada.Text_IO, Ada.Integer_Text_IO;

procedure LoopDemo is

   Count : INTEGER;

begin

   Count := 1;
   while Count < 5 loop           
      Put("Count =");
      Put(Count, 5); 
      New_Line;
      Count := Count + 1;
   end loop;

end LoopDemo;
   