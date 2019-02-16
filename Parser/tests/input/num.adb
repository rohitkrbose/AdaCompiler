with Gnat.Io; use Gnat.Io;
procedure Numbers is
   Mike, Alice: Integer;
   John_Smith: Integer;
begin
   Put("Enter a number Mike: ");
   Get(Mike);
   John_Smith := 3 * Mike;
   Put("3*Mike + 2*Alice + 11 is ");
   Put(John_Smith);
   New_Line;
end Numbers;