with Text_IO;
with Gnat.Io; use Gnat.Io;
procedure Calc is
   Op: Integer;         
   Disp: Integer := 0;    
   In_Val: Integer;       
begin
   loop
      Put("> ");
      Get(In_Val);
      Text_IO.Skip_Line;
      case Op is
         when 1      => Disp := In_Val;
         when 2      => Disp := Disp + In_Val;
         when others   => Put_Line("What is ");
      end case;
   end loop;
end Calc;