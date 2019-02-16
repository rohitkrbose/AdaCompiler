with Gnat.Io; use Gnat.Io;
procedure ll is                      
   type Node_Ptr is access Node;    

   type Node is record              
      Data: Integer;
   end record;                               
   In_Int: Integer;  

begin
   exit when In_Int = -1;
   New_Node.Next := null;
   Scan_Ptr := Head;
end ll;